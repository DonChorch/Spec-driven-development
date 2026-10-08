"""
Tablero de tareas de Spec-Driven Development.

Lee sdd/specs/*/tasks.md (la fuente de verdad) y lo muestra por etapas (secciones "## " de tasks.md) en
http://127.0.0.1:5070. La página se actualiza sola cuando cambia un tasks.md, una especificación o una nota.
Las notas se guardan en sdd/tablero/notas.json, dentro del proyecto.

Uso (desde la raíz del proyecto, o con --raiz):
  python <skill>/scripts/tablero.py                        levanta el tablero (solo 127.0.0.1)
  python <skill>/scripts/tablero.py --puerto 5071          en otro puerto
  python <skill>/scripts/tablero.py nota 010 T16 "texto"   agrega una nota a una tarea (la usa el agente al avanzarla)
  python <skill>/scripts/tablero.py resumen 010            estado por etapa, en texto

Estado de cada tarea (se deduce de tasks.md): hecha ([x]) · falta revisión (la verificación dice "falta la revisión")
· espera a otra persona (columna Quién distinta del agente) · bloqueada (depende de una tarea sin hacer) · pendiente.

Solo biblioteca estándar. No escucha en la red: únicamente 127.0.0.1.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
import sys
import threading
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
# La página: junto al script (copia en un proyecto) o en assets/tablero de la skill.
PAGINA = next((p for p in (AQUI / "tablero.html", AQUI.parent / "assets" / "tablero" / "tablero.html") if p.exists()),
              AQUI / "tablero.html")
# Quién es "el agente" en la columna Quién (lo demás es una persona: DBA, la persona responsable, etc.).
AGENTES = ("claude", "agente", "ia")
SDD = Path.cwd() / "sdd"
SPECS = SDD / "specs"
NOTAS = SDD / "tablero" / "notas.json"
_bloqueo = threading.Lock()


def configurar(raiz: Path) -> None:
    global SDD, SPECS, NOTAS
    SDD = raiz.resolve() / "sdd"
    SPECS = SDD / "specs"
    NOTAS = SDD / "tablero" / "notas.json"
    if not SPECS.is_dir():
        sys.exit(f"No se encontró {SPECS}. Ejecutá desde la raíz del proyecto o usá --raiz.")


def proyecto() -> str:
    """Nombre del proyecto: "**Sistema:**" o "**Proyecto:**" de la constitución, o el título del índice."""
    c = SDD / "constitution.md"
    if c.exists() and (m := re.search(r"^\*\*(?:Sistema|Proyecto):\*\*\s*(.+)$", c.read_text(encoding="utf-8"), re.M)):
        return m.group(1).strip()
    r = SDD / "README.md"
    if r.exists() and (m := re.search(r"^#\s+(?:Especificaciones\s*(?:·|del|de)?\s*)?(.+)$", r.read_text(encoding="utf-8"), re.M)):
        return re.sub(r"\s*\(.*?\)\s*$", "", m.group(1)).strip()
    return SDD.parent.name

ESTADOS = {
    "hecha": "Hecha",
    "revision": "Falta revisión",
    "espera": "Espera a otra persona",
    "bloqueada": "Bloqueada por otra tarea",
    "pendiente": "Pendiente",
}


# ---------------------------------------------------------------- lectura de las especificaciones

def specs() -> list[dict]:
    salida = []
    for d in sorted(p for p in SPECS.iterdir() if p.is_dir()):
        m = re.match(r"(\d{3})-", d.name)
        if not m:
            continue
        titulo, estado, fase = d.name, "", ""
        f = d / "specification.md"
        if f.exists():
            t = f.read_text(encoding="utf-8")
            if (x := re.search(r"^#\s+(.+)$", t, re.M)):
                titulo = x.group(1).strip()
            if (x := re.search(r"^\|\s*Estado\s*\|\s*([^|]+)\|", t, re.M)):
                estado = x.group(1).strip()
            if (x := re.search(r"^\|\s*Fase\s*\|\s*([^|]+)\|", t, re.M)):
                fase = x.group(1).strip()
        salida.append({"id": m.group(1), "carpeta": d.name, "titulo": titulo, "estado": estado, "fase": fase})
    return salida


def carpeta_de(nnn: str) -> Path | None:
    for d in SPECS.iterdir():
        if d.is_dir() and d.name.startswith(nnn + "-"):
            return d
    return None


def celdas(linea: str) -> list[str]:
    # separa por "|" que no estén dentro de `código`
    partes, actual, en_codigo = [], "", False
    for ch in linea.strip().strip("|"):
        if ch == "`":
            en_codigo = not en_codigo
        if ch == "|" and not en_codigo:
            partes.append(actual.strip())
            actual = ""
        else:
            actual += ch
    partes.append(actual.strip())
    return partes


def expandir_dependencias(texto: str) -> tuple[list[str], list[str]]:
    """'T05…T08, T15' → ['T05','T06','T07','T08','T15']; lo que no es una tarea local queda como externo."""
    internas, externas = [], []
    for parte in re.split(r",\s*", texto.strip()):
        parte = parte.strip()
        if not parte or parte in ("—", "-"):
            continue
        if (m := re.fullmatch(r"T(\d+)\s*(?:…|\.\.\.|–|-)\s*T(\d+)", parte)):
            a, b = int(m.group(1)), int(m.group(2))
            internas += [f"T{n:02d}" for n in range(a, b + 1)]
        elif re.fullmatch(r"T\d+", parte):
            internas.append(parte)
        else:
            externas.append(parte)
    return internas, externas


def leer_tareas(carpeta: Path) -> dict:
    archivo = carpeta / "tasks.md"
    texto = archivo.read_text(encoding="utf-8") if archivo.exists() else ""
    etapas, etapa, encabezado = [], None, None
    for linea in texto.splitlines():
        if linea.startswith("## "):
            etapa = {"titulo": linea[3:].strip(), "tareas": []}
            etapas.append(etapa)
            encabezado = None
            continue
        if not linea.startswith("|"):
            continue
        c = celdas(linea)
        if len(c) > 2 and c[1] == "Id":
            encabezado = [x.lower() for x in c]
            continue
        if not encabezado or not re.fullmatch(r"\[[ x]\]", c[0] or ""):
            continue
        fila = dict(zip(encabezado, c))
        if etapa is None:
            etapa = {"titulo": "Tareas", "tareas": []}
            etapas.append(etapa)
        internas, externas = expandir_dependencias(fila.get("depende de", ""))
        etapa["tareas"].append({
            "hecha": c[0] == "[x]",
            "id": fila.get("id", ""),
            "tarea": fila.get("tarea", ""),
            "quien": fila.get("quién", "") or "Agente",
            "depende": internas,
            "dependeExterno": externas,
            "cubre": fila.get("cubre", ""),
            "verificacion": fila.get("verificación", ""),
        })
    todas = {t["id"]: t for e in etapas for t in e["tareas"]}
    for t in todas.values():
        t["estado"] = estado_de(t, todas)
        v = t["verificacion"].lower()
        t["sinProbar"] = t["hecha"] and ("sin ejecutar" in v or "no probado" in v or "no se probó" in v)
    return {"etapas": etapas, "archivo": str(archivo.relative_to(SDD.parent))}


def estado_de(t: dict, todas: dict) -> str:
    if t["hecha"]:
        return "hecha"
    if any(x in t["verificacion"].lower() for x in ("falta la revisión", "falta revisión", "pendiente de revisión")):
        return "revision"
    if not t["quien"].lower().startswith(AGENTES):
        return "espera"
    if any(d in todas and not todas[d]["hecha"] for d in t["depende"]):
        return "bloqueada"
    return "pendiente"


# ---------------------------------------------------------------- notas

def leer_notas() -> dict:
    if not NOTAS.exists():
        return {}
    try:
        return json.loads(NOTAS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def agregar_nota(nnn: str, tarea: str, texto: str, autor: str, origen: str) -> dict:
    texto = texto.strip()
    if not texto or len(texto) > 2000:
        raise ValueError("La nota tiene que tener entre 1 y 2000 caracteres.")
    if not re.fullmatch(r"\d{3}", nnn) or not re.fullmatch(r"T\d+", tarea):
        raise ValueError("Especificación o tarea inválida.")
    nota = {"fecha": datetime.now().isoformat(timespec="seconds"), "autor": autor[:100], "origen": origen, "texto": texto}
    with _bloqueo:
        notas = leer_notas()
        notas.setdefault(nnn, {}).setdefault(tarea, []).append(nota)
        NOTAS.parent.mkdir(parents=True, exist_ok=True)
        tmp = NOTAS.with_suffix(".tmp")
        tmp.write_text(json.dumps(notas, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, NOTAS)
    return nota


# ---------------------------------------------------------------- vista de una especificación

def vista(nnn: str) -> dict | None:
    carpeta = carpeta_de(nnn)
    if carpeta is None:
        return None
    datos = leer_tareas(carpeta)
    notas = leer_notas().get(nnn, {})
    conteo = {k: 0 for k in ESTADOS}
    for e in datos["etapas"]:
        for t in e["tareas"]:
            t["notas"] = notas.get(t["id"], [])
            conteo[t["estado"]] += 1
        e["hechas"] = sum(t["hecha"] for t in e["tareas"])
    info = next((s for s in specs() if s["id"] == nnn), {})
    return {**info, **datos, "conteo": conteo, "total": sum(conteo.values()), "estados": ESTADOS}


def huella(nnn: str) -> str:
    """Cambia cuando cambia el tasks.md, la especificación o las notas: la página la usa para refrescarse sola."""
    h = hashlib.sha256()
    carpeta = carpeta_de(nnn)
    for f in ([carpeta / "tasks.md", carpeta / "specification.md"] if carpeta else []) + [NOTAS]:
        if f.exists():
            h.update(f"{f}:{f.stat().st_mtime_ns}:{f.stat().st_size}".encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- servidor

class Manejador(BaseHTTPRequestHandler):
    server_version = "TableroSDD"

    def log_message(self, fmt, *args):  # sin ruido en la consola
        pass

    def _json(self, codigo: int, datos, extra: dict | None = None):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _host_valido(self) -> bool:
        """Rechaza otros nombres de host (DNS rebinding): solo se acepta localhost o 127.0.0.1."""
        host = self.headers.get("Host", "").rsplit(":", 1)[0].strip("[]").lower()
        return host in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self._host_valido():
            return self._json(403, {"error": "Host no permitido."})
        ruta = self.path.split("?")[0]
        if ruta == "/":
            cuerpo = PAGINA.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(cuerpo)
            return
        if ruta == "/api/specs":
            return self._json(200, specs())
        if ruta == "/api/info":
            return self._json(200, {"proyecto": proyecto()})
        if (m := re.fullmatch(r"/api/spec/(\d{3})/huella", ruta)):
            return self._json(200, {"huella": huella(m.group(1))})
        if (m := re.fullmatch(r"/api/spec/(\d{3})", ruta)):
            v = vista(m.group(1))
            return self._json(200, {**v, "huella": huella(m.group(1))}) if v else self._json(404, {"error": "No existe esa especificación."})
        self._json(404, {"error": "No encontrado."})

    def do_POST(self):
        if not self._host_valido():
            return self._json(403, {"error": "Host no permitido."})
        # Solo la propia página: exige una cabecera que otro sitio no puede mandar sin un preflight que acá no se responde.
        if self.headers.get("X-Tablero") != "1":
            return self._json(403, {"error": "Falta X-Tablero."})
        m = re.fullmatch(r"/api/spec/(\d{3})/notas", self.path)
        if not m:
            return self._json(404, {"error": "No encontrado."})
        try:
            largo = min(int(self.headers.get("Content-Length", "0")), 10_000)
            d = json.loads(self.rfile.read(largo) or b"{}")
            nota = agregar_nota(m.group(1), str(d.get("tarea", "")), str(d.get("texto", "")),
                                autor=getpass.getuser(), origen="persona")
            self._json(201, nota)
        except (ValueError, json.JSONDecodeError) as e:
            self._json(400, {"error": str(e)})


def resumen(nnn: str) -> None:
    v = vista(nnn)
    if not v:
        sys.exit(f"No existe la especificación {nnn}.")
    print(f"{v['titulo']} · {v['conteo']['hecha']}/{v['total']} hechas")
    for e in v["etapas"]:
        print(f"\n{e['titulo']}  ({e['hechas']}/{len(e['tareas'])})")
        for t in e["tareas"]:
            print(f"  {t['id']:<4} {ESTADOS[t['estado']]:<26} {t['quien']:<8} {re.sub(r'[`*]', '', t['tarea'])[:80]}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Tablero de tareas de Spec-Driven Development")
    sub = p.add_subparsers(dest="cmd")
    p.add_argument("--puerto", type=int, default=5070)
    p.add_argument("--raiz", type=Path, default=Path.cwd(), help="raíz del proyecto (la que contiene sdd/)")
    n = sub.add_parser("nota", help="agrega una nota a una tarea")
    n.add_argument("spec"); n.add_argument("tarea"); n.add_argument("texto")
    n.add_argument("--autor", default="Claude", help="quién escribe la nota (por defecto, el agente)")
    r = sub.add_parser("resumen", help="estado por etapa, en texto")
    r.add_argument("spec")
    a = p.parse_args()
    configurar(a.raiz)

    if a.cmd == "nota":
        nota = agregar_nota(a.spec, a.tarea.upper(), a.texto, autor=a.autor, origen="claude" if a.autor == "Claude" else "persona")
        print(f"Nota agregada a {a.spec} {a.tarea.upper()} ({nota['fecha']}).")
        return
    if a.cmd == "resumen":
        resumen(a.spec)
        return

    srv = ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador)
    print(f"Tablero de {proyecto()} en http://127.0.0.1:{a.puerto}  (Ctrl+C para detener)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
