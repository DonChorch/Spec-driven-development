#!/usr/bin/env python3
"""Herramienta de Spec-Driven Development (sin dependencias externas).

Uso:
  python sdd.py init     [--raiz RUTA] [--proyecto NOMBRE]   crea sdd/ con constitución, plantillas e índice
  python sdd.py nueva    "Título" [--raiz RUTA]               crea sdd/specs/NNN-titulo/ y lo suma al índice
  python sdd.py validar  [NNN] [--raiz RUTA]                  controla calidad y trazabilidad (código 1 si hay errores)
  python sdd.py estado   [--raiz RUTA]                        resumen de cada especificación (estado, fase, avance)

La raíz es la carpeta del proyecto (la que contiene sdd/). Por defecto, la carpeta actual o la primera hacia arriba que tenga sdd/.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PLANTILLAS = AQUI.parent / "assets" / "plantillas"

ESTADOS = ["borrador", "aclarando", "planificada", "en curso", "implementada", "en producción"]
# Fase mínima esperada para cada estado (para detectar incoherencias).
FASE_POR_ESTADO = {"borrador": 1, "aclarando": 2, "planificada": 3, "en curso": 5, "implementada": 5, "en producción": 6}

ID = re.compile(r"\b(RF|RNF|CA|HU|AC|T)-?(\d{1,3})\b")
RANGO = re.compile(r"\b(RF|RNF|CA|HU)-(\d{1,3})\s*(?:…|\.\.\.|a|-)\s*(\d{1,3})\b")


def sin_acentos(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def buscar_raiz(inicio: Path) -> Path:
    p = inicio.resolve()
    for c in [p, *p.parents]:
        if (c / "sdd").is_dir():
            return c
    return p


# ---------------------------------------------------------------- lectura de documentos
def filas(texto: str, seccion: str) -> list[list[str]]:
    """Filas de la primera tabla que aparece bajo el encabezado que contiene `seccion`."""
    lineas = texto.splitlines()
    dentro, tabla = False, []
    for ln in lineas:
        if ln.startswith("#"):
            if dentro and tabla:
                break
            dentro = seccion in sin_acentos(ln)
            continue
        if dentro and ln.strip().startswith("|"):
            celdas = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in celdas):
                continue
            tabla.append(celdas)
        elif dentro and tabla and not ln.strip():
            continue
    return tabla[1:] if tabla else []   # sin la fila de encabezado


def metadatos(texto: str) -> dict[str, str]:
    m = {}
    for ln in texto.splitlines()[:25]:
        r = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$", ln)
        if r and r.group(1).lower() not in ("campo", "---"):
            m[sin_acentos(r.group(1))] = r.group(2)
    return m


def ids_en(texto: str, tipos: set[str]) -> set[str]:
    encontrados = set()
    for t, a, b in RANGO.findall(texto):
        if t in tipos:
            for n in range(int(a), int(b) + 1):
                encontrados.add(f"{t}-{n:02d}")
    for t, n in ID.findall(texto):
        if t in tipos:
            encontrados.add(f"{t}-{int(n):02d}")
    return encontrados


def norm(i: str) -> str:
    t, n = i.split("-")
    return f"{t}-{int(n):02d}"


@dataclass
class Hallazgos:
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def error(self, m: str) -> None: self.errores.append(m)
    def aviso(self, m: str) -> None: self.avisos.append(m)


@dataclass
class Spec:
    carpeta: Path
    numero: str
    texto: str
    meta: dict[str, str]

    @property
    def estado(self) -> str:
        e = sin_acentos(self.meta.get("estado", ""))
        return next((x for x in ESTADOS if sin_acentos(x) in e), "")

    @property
    def fase(self) -> int:
        m = re.match(r"\s*(\d)", self.meta.get("fase", ""))
        return int(m.group(1)) if m else 0

    @property
    def titulo(self) -> str:
        m = re.search(r"^#\s+(.+)$", self.texto, re.M)
        if not m:
            return self.carpeta.name
        return re.sub(r"^\d{3}\s*·\s*", "", m.group(1).strip())


def cargar(raiz: Path) -> list[Spec]:
    specs = []
    base = raiz / "sdd" / "specs"
    if not base.is_dir():
        return specs
    for c in sorted(base.iterdir()):
        f = c / "specification.md"
        if c.is_dir() and f.is_file():
            t = f.read_text(encoding="utf-8")
            specs.append(Spec(c, c.name.split("-")[0], t, metadatos(t)))
    return specs


# ---------------------------------------------------------------- validación
def validar_spec(s: Spec, h: Hallazgos) -> None:
    p = s.numero
    if not s.estado:
        h.error(f"{p}: falta el Estado (o no es uno de: {', '.join(ESTADOS)})")
    if not s.fase:
        h.error(f"{p}: falta la Fase (número de 1 a 6)")
    if s.estado and s.fase and s.fase < FASE_POR_ESTADO[s.estado] - 1:
        h.aviso(f"{p}: estado '{s.estado}' con fase {s.fase}: revisar que sean coherentes")

    rf_filas = filas(s.texto, "requisitos funcionales")
    rnf_filas = filas(s.texto, "requisitos no funcionales")
    ca_filas = filas(s.texto, "criterios de aceptacion")
    ac_filas = filas(s.texto, "aclaraciones")

    def ids_de(tabla: list[list[str]], prefijo: str) -> list[str]:
        r = []
        for f in tabla:
            m = re.match(rf"^\**({prefijo})-(\d+)", f[0]) if f else None
            if m:
                r.append(f"{prefijo}-{int(m.group(2)):02d}")
        return r

    rf, rnf, ca = ids_de(rf_filas, "RF"), ids_de(rnf_filas, "RNF"), ids_de(ca_filas, "CA")
    hu = ids_en(s.texto, {"HU"})
    for nombre, lista in (("RF", rf), ("RNF", rnf), ("CA", ca)):
        dup = {x for x in lista if lista.count(x) > 1}
        if dup:
            h.error(f"{p}: ids repetidos: {', '.join(sorted(dup))}")
    if s.fase >= 1 and not rf:
        h.error(f"{p}: no tiene requisitos funcionales (RF-NN)")
    if s.fase >= 2 and not ca:
        h.error(f"{p}: fase {s.fase} sin criterios de aceptación (CA-NN)")

    # Restos de plantilla: requisitos vacíos o criterios con "…"
    for f in rf_filas + rnf_filas:
        if f and re.match(r"^\**(RF|RNF)-\d+", f[0]) and len(f) > 1 and len(f[1].strip()) < 5:
            (h.error if s.fase >= 2 else h.aviso)(f"{p}: {f[0].strip('* ')} está vacío (resto de la plantilla)")
    for f in ca_filas:
        if f and re.match(r"^\**CA-\d+", f[0]) and "…" in " ".join(f[1:2]):
            (h.error if s.fase >= 2 else h.aviso)(f"{p}: {f[0].strip('* ')} todavía tiene los '…' de la plantilla")

    conocidos = set(rf) | set(rnf) | hu
    cubiertos: set[str] = set()
    for f in ca_filas:
        if not f or not re.match(r"^\**CA-\d+", f[0]):
            continue
        cid = norm(re.match(r"^\**(CA-\d+)", f[0]).group(1))
        texto = " ".join(f[1:])
        tx = sin_acentos(texto)
        if not ("dado" in tx and "cuando" in tx and "entonces" in tx) and not ("dado" in tx and "entonces" in tx):
            h.error(f"{p}: {cid} no está escrito como Dado / Cuando / Entonces")
        refs = ids_en(texto, {"RF", "RNF", "HU"})
        if not refs:
            h.error(f"{p}: {cid} no dice qué requisito cubre")
        for r in refs - conocidos:
            h.error(f"{p}: {cid} cubre {r}, que no existe en la especificación")
        cubiertos |= refs

    if s.fase >= 3:
        for f in rf_filas:
            m = re.match(r"^\**(RF-\d+)", f[0]) if f else None
            prioridad = sin_acentos(f[-1]).strip(" *") if f else ""
            if m and prioridad == "debe" and norm(m.group(1)) not in cubiertos:
                h.aviso(f"{p}: {norm(m.group(1))} es 'Debe' y ningún criterio de aceptación lo cubre")

    # Aclaraciones abiertas que bloquean: convención "Abierta · bloquea RF-NN" (o RNF / CA)
    bloquea = re.compile(r"bloquea\s+(RF|RNF|CA)-?\d+", re.I)
    bloqueantes = [f[0] for f in ac_filas if f and "abierta" in sin_acentos(" ".join(f)) and bloquea.search(" ".join(f))]
    if bloqueantes and s.fase >= 3:
        h.error(f"{p}: está en fase {s.fase} con aclaraciones abiertas que bloquean: {', '.join(bloqueantes)}")
    elif bloqueantes:
        h.aviso(f"{p}: aclaraciones abiertas que bloquean el paso a Planificar: {', '.join(bloqueantes)}")

    if "cumplimiento de la constitucion" not in sin_acentos(s.texto):
        h.aviso(f"{p}: falta la sección 'Cumplimiento de la constitución'")

    # Plan y tareas
    plan, tareas = s.carpeta / "plan.md", s.carpeta / "tasks.md"
    if s.fase >= 3 and not plan.is_file():
        h.error(f"{p}: fase {s.fase} sin plan.md")
    if s.fase >= 4 and not tareas.is_file():
        h.error(f"{p}: fase {s.fase} sin tasks.md")
    if tareas.is_file():
        validar_tareas(s, tareas.read_text(encoding="utf-8"), set(rf) | set(rnf) | set(ca) | hu, h)


def validar_tareas(s: Spec, texto: str, conocidos: set[str], h: Hallazgos) -> None:
    p = s.numero
    lineas = [ln for ln in texto.splitlines() if ln.strip().startswith("|")]
    if not lineas:
        h.aviso(f"{p}: tasks.md no tiene tabla de tareas")
        return
    enc = [sin_acentos(c.strip()) for c in lineas[0].strip().strip("|").split("|")]
    def col(nombre: str) -> int | None:
        return next((i for i, c in enumerate(enc) if nombre in c), None)
    i_cubre, i_verif, i_id = col("cubre"), col("verific"), col("id")
    for nombre, i in (("Cubre", i_cubre), ("Verificación", i_verif), ("Id", i_id)):
        if i is None:
            h.aviso(f"{p}: tasks.md no tiene la columna '{nombre}': no se puede controlar")
    for ln in lineas[1:]:
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if all(set(x) <= set("-: ") for x in c):
            continue
        tid = c[i_id] if i_id is not None and i_id < len(c) else "?"
        hecha = "[x]" in c[0].lower()
        if i_cubre is not None and i_cubre < len(c):
            for r in ids_en(c[i_cubre], {"RF", "RNF", "CA", "HU"}) - conocidos:
                h.error(f"{p}: {tid} cubre {r}, que no existe en la especificación")
        if hecha:
            v = c[i_verif] if i_verif is not None and i_verif < len(c) else ""
            if len(v.strip()) < 3:
                h.error(f"{p}: {tid} está marcada como hecha sin decir cómo se verificó")


def validar_indice(raiz: Path, specs: list[Spec], h: Hallazgos) -> None:
    readme = raiz / "sdd" / "README.md"
    if not readme.is_file():
        h.aviso("falta sdd/README.md (índice)")
        return
    texto = readme.read_text(encoding="utf-8")
    for s in specs:
        fila = next((ln for ln in texto.splitlines() if re.match(rf"\|\s*{s.numero}\s*\|", ln)), None)
        if not fila:
            h.error(f"índice: falta la especificación {s.numero}")
            continue
        if s.estado and sin_acentos(s.estado) not in sin_acentos(fila):
            h.aviso(f"índice: {s.numero} figura con otro estado (en la especificación: '{s.estado}')")
    if not (raiz / "sdd" / "constitution.md").is_file():
        h.error("falta sdd/constitution.md")


# ---------------------------------------------------------------- comandos
def cmd_init(raiz: Path, proyecto: str) -> int:
    sdd = raiz / "sdd"
    if (sdd / "constitution.md").exists():
        print(f"Ya existe {sdd / 'constitution.md'}: no se sobrescribe nada.")
        return 0
    (sdd / "specs").mkdir(parents=True, exist_ok=True)
    shutil.copytree(PLANTILLAS, sdd / "plantillas", dirs_exist_ok=True)
    hoy = date.today().isoformat()
    const = (PLANTILLAS / "constitution.md").read_text(encoding="utf-8").replace("{{PROYECTO}}", proyecto).replace("{{FECHA}}", hoy)
    (sdd / "constitution.md").write_text(const, encoding="utf-8")
    (sdd / "plantillas" / "constitution.md").unlink(missing_ok=True)
    readme = (AQUI.parent / "assets" / "README.md").read_text(encoding="utf-8").replace("{{PROYECTO}}", proyecto)
    (sdd / "README.md").write_text(readme, encoding="utf-8")
    print(f"Estructura creada en {sdd}. Siguiente paso: completar la constitución (fase 0) con el equipo.")
    return 0


def slug(t: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", sin_acentos(t)).strip("-")
    return "-".join(s.split("-")[:6]) or "spec"


def cmd_nueva(raiz: Path, titulo: str) -> int:
    base = raiz / "sdd" / "specs"
    if not base.is_dir():
        print("No hay sdd/specs: primero `sdd.py init`.", file=sys.stderr)
        return 1
    nums = [int(c.name[:3]) for c in base.iterdir() if c.is_dir() and c.name[:3].isdigit()]
    n = f"{(max(nums) + 1) if nums else 1:03d}"
    carpeta = base / f"{n}-{slug(titulo)}"
    carpeta.mkdir()
    origen = raiz / "sdd" / "plantillas"
    if not origen.is_dir():
        origen = PLANTILLAS
    hoy = date.today().isoformat()
    for nombre in ("specification.md", "plan.md", "tasks.md"):
        t = (origen / nombre).read_text(encoding="utf-8").replace("NNN", n).replace("Título de la especificación", titulo).replace("AAAA-MM-DD", hoy)
        (carpeta / nombre).write_text(t, encoding="utf-8")
    readme = raiz / "sdd" / "README.md"
    if readme.is_file():
        t = readme.read_text(encoding="utf-8").rstrip("\n").split("\n")
        fila = f"| {n} | [{titulo}](specs/{carpeta.name}/specification.md) | Borrador | 1 | |"
        idx = max((i for i, ln in enumerate(t) if re.match(r"\|\s*\d{3}\s*\|", ln)), default=None)
        if idx is None:
            idx = max((i for i, ln in enumerate(t) if ln.startswith("|---") or ln.startswith("| ---")), default=len(t) - 1)
        t.insert(idx + 1, fila)
        readme.write_text("\n".join(t) + "\n", encoding="utf-8")
    print(f"Creada {carpeta.relative_to(raiz)} (fase 1 · Borrador). Completá specification.md antes de planificar.")
    return 0


def cmd_validar(raiz: Path, solo: str | None) -> int:
    specs = cargar(raiz)
    if solo:
        specs = [s for s in specs if s.numero == solo.zfill(3)]
        if not specs:
            print(f"No existe la especificación {solo}.", file=sys.stderr)
            return 1
    h = Hallazgos()
    for s in specs:
        validar_spec(s, h)
    if not solo:
        validar_indice(raiz, specs, h)
    for e in h.errores:
        print(f"ERROR  {e}")
    for a in h.avisos:
        print(f"AVISO  {a}")
    print(f"\n{len(specs)} especificaciones revisadas · {len(h.errores)} errores · {len(h.avisos)} avisos")
    return 1 if h.errores else 0


def cmd_estado(raiz: Path) -> int:
    specs = cargar(raiz)
    if not specs:
        print("No hay especificaciones.")
        return 0
    print(f"{'#':<4} {'Estado':<14} {'Fase':<5} {'Tareas':<8} Título")
    for s in specs:
        t = s.carpeta / "tasks.md"
        hechas = total = 0
        if t.is_file():
            for ln in t.read_text(encoding="utf-8").splitlines():
                if re.match(r"\|\s*\[( |x|X)\]", ln):
                    total += 1
                    hechas += "[x]" in ln.lower()
        print(f"{s.numero:<4} {s.estado or '?':<14} {s.fase or '?':<5} {f'{hechas}/{total}':<8} {s.titulo}")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Spec-Driven Development")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("init", "nueva", "validar", "estado"):
        sp = sub.add_parser(n)
        sp.add_argument("--raiz", type=Path, default=None)
        if n == "init":
            sp.add_argument("--proyecto", default="Proyecto")
        if n == "nueva":
            sp.add_argument("titulo")
        if n == "validar":
            sp.add_argument("numero", nargs="?")
    a = ap.parse_args()
    raiz = a.raiz.resolve() if a.raiz else (Path.cwd() if a.cmd == "init" else buscar_raiz(Path.cwd()))
    if a.cmd == "init":
        return cmd_init(raiz, a.proyecto)
    if a.cmd == "nueva":
        return cmd_nueva(raiz, a.titulo)
    if a.cmd == "validar":
        return cmd_validar(raiz, a.numero)
    return cmd_estado(raiz)


if __name__ == "__main__":
    sys.exit(main())
