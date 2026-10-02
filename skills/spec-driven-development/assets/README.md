# Especificaciones · {{PROYECTO}}

Spec-Driven Development: **la especificación es la fuente de verdad**. El código, las pruebas y los documentos se derivan de ella y se validan contra ella. Si el código y la especificación no coinciden, se corrige uno de los dos a propósito, nunca en silencio.

```
sdd/
├── constitution.md        principios permanentes
├── README.md              este índice
├── plantillas/            specification.md · plan.md · tasks.md
└── specs/NNN-nombre/      specification.md · plan.md · tasks.md
```

## Flujo
| Fase | Qué se hace | Sale con |
|---|---|---|
| 0 · Constitución | Principios, stack y reglas | `constitution.md` aprobada |
| 1 · Especificar | Qué y por qué, sin tecnología | Historias, requisitos y criterios de aceptación |
| 2 · Aclarar | Ambigüedades y decisiones de otros | Ninguna aclaración que bloquee |
| 3 · Planificar | Diseño trazable a los requisitos | `plan.md` |
| 4 · Tareas | Tareas chicas, ordenadas por dependencia | `tasks.md` |
| 5 · Implementar | Construir y verificar cada tarea | Código, pruebas y tareas `[x]` |
| 6 · Iterar | Lo aprendido vuelve a la especificación | Nueva revisión |

Control de calidad: `python <skill>/scripts/sdd.py validar`.

Tablero de tareas por etapa, con notas: `python <skill>/scripts/tablero.py`, en http://127.0.0.1:5070.

## Índice
| # | Especificación | Estado | Fase | Notas |
|---|---|---|---|---|
