#!/usr/bin/env python3
"""Arma dist/spec-driven-development.skill desde skills/spec-driven-development.

  python build.py           regenera el paquete
  python build.py --check   falla (código 1) si el paquete no coincide con el código fuente
"""
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "skills" / "spec-driven-development"
DESTINO = RAIZ / "dist" / "spec-driven-development.skill"


def archivos():
    return sorted(p for p in ORIGEN.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")


def main() -> int:
    if "--check" in sys.argv:
        if not DESTINO.exists():
            print("Falta el paquete en dist/.")
            return 1
        with zipfile.ZipFile(DESTINO) as z:
            guardado = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
        esperado = {f"spec-driven-development/{p.relative_to(ORIGEN).as_posix()}": p.read_bytes() for p in archivos()}
        distintos = sorted(n for n in guardado.keys() | esperado.keys() if guardado.get(n) != esperado.get(n))
        for n in distintos:
            print(f"desactualizado: {n}")
        return 1 if distintos else 0
    DESTINO.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as z:
        for p in archivos():
            z.write(p, f"spec-driven-development/{p.relative_to(ORIGEN).as_posix()}")
    print(f"Generado {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
