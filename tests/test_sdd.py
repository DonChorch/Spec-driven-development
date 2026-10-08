import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "skills" / "spec-driven-development" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sdd  # noqa: E402
import tablero  # noqa: E402

SPEC = """# 001 · Demo

| Campo | Valor |
|---|---|
| Estado | Planificada |
| Fase | 3 |

## Requisitos funcionales
| Id | Requisito | Prioridad |
|---|---|---|
| RF-01 | El usuario puede darse de alta | Debe |
| RF-02 | El usuario puede borrarse | Debe |

## Criterios de aceptación
| Id | Criterio | Cubre | Verificación |
|---|---|---|---|
| CA-01 | Dado un mail nuevo, cuando se registra, entonces queda creado | RF-01 | prueba |
| CA-02 | Dado un usuario, cuando borra, entonces desaparece | RF-09 | prueba |

## Aclaraciones
| Id | Pregunta | Estado |
|---|---|---|
| AC-01 | ¿Plazo? | Abierta · bloquea RF-02 |

## Cumplimiento de la constitución
- [x] ok
"""
TAREAS = """# Tareas
## Etapa 1
| | Id | Tarea | Depende de | Cubre | Verificación |
|---|---|---|---|---|---|
| [x] | T01 | a | — | RF-01 | |
| [ ] | T02 | b | T01 | RF-77 | |
"""


def proyecto(tmp: Path) -> Path:
    (tmp / "sdd" / "specs" / "001-demo").mkdir(parents=True)
    (tmp / "sdd" / "constitution.md").write_text("x", encoding="utf-8")
    (tmp / "sdd" / "README.md").write_text("| # | E | Estado | F | N |\n|---|---|---|---|---|\n| 001 | d | Planificada | 3 | |\n", encoding="utf-8")
    d = tmp / "sdd" / "specs" / "001-demo"
    (d / "specification.md").write_text(SPEC, encoding="utf-8")
    (d / "plan.md").write_text("plan", encoding="utf-8")
    (d / "tasks.md").write_text(TAREAS, encoding="utf-8")
    return tmp


class Validador(unittest.TestCase):
    def test_detecta_errores_de_trazabilidad(self):
        with tempfile.TemporaryDirectory() as t:
            raiz = proyecto(Path(t))
            h = sdd.Hallazgos()
            for s in sdd.cargar(raiz):
                sdd.validar_spec(s, h)
            texto = "\n".join(h.errores)
            self.assertIn("CA-02 cubre RF-09", texto)
            self.assertIn("aclaraciones abiertas que bloquean", texto)
            self.assertIn("T01 está marcada como hecha sin decir cómo", texto)
            self.assertIn("T02 cubre RF-77", texto)

    def test_estado_y_titulo(self):
        with tempfile.TemporaryDirectory() as t:
            s = sdd.cargar(proyecto(Path(t)))[0]
            self.assertEqual((s.estado, s.fase, s.titulo), ("planificada", 3, "Demo"))

    def test_init_nueva_validar(self):
        with tempfile.TemporaryDirectory() as t:
            cli = [sys.executable, "-I", str(SCRIPTS / "sdd.py")]
            for args in (["init", "--proyecto", "X"], ["nueva", "Alta de usuarios"]):
                r = subprocess.run(cli + args, cwd=t, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(t) / "sdd/specs/001-alta-de-usuarios/tasks.md").is_file())
            self.assertEqual(subprocess.run(cli + ["validar"], cwd=t, capture_output=True).returncode, 0)

    def test_tareas_sin_columnas_avisa(self):
        h = sdd.Hallazgos()
        s = sdd.Spec(Path("."), "001", "", {})
        sdd.validar_tareas(s, "| a | b |\n|---|---|\n| [x] | y |\n", set(), h)
        self.assertTrue(any("columna" in a for a in h.avisos))


class Tablero(unittest.TestCase):
    def test_dependencias(self):
        self.assertEqual(tablero.expandir_dependencias("T05…T07, T09, DBA"), (["T05", "T06", "T07", "T09"], ["DBA"]))

    def test_estados(self):
        with tempfile.TemporaryDirectory() as t:
            raiz = proyecto(Path(t))
            tablero.configurar(raiz)
            datos = tablero.leer_tareas(raiz / "sdd/specs/001-demo")
            est = {x["id"]: x["estado"] for e in datos["etapas"] for x in e["tareas"]}
            self.assertEqual(est, {"T01": "hecha", "T02": "pendiente"})

    def test_host_rechazado(self):
        with tempfile.TemporaryDirectory() as t:
            tablero.configurar(proyecto(Path(t)))
            srv = tablero.ThreadingHTTPServer(("127.0.0.1", 0), tablero.Manejador)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            url = f"http://127.0.0.1:{srv.server_address[1]}/api/specs"
            try:
                self.assertEqual(urllib.request.urlopen(url).status, 200)
                with self.assertRaises(urllib.error.HTTPError) as e:
                    urllib.request.urlopen(urllib.request.Request(url, headers={"Host": "evil.com"}))
                self.assertEqual(e.exception.code, 403)
            finally:
                srv.shutdown()


class Paquete(unittest.TestCase):
    def test_dist_actualizado(self):
        r = subprocess.run([sys.executable, str(RAIZ / "build.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
