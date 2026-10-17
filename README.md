# Spec-Driven Development · skills para Claude

Skills para trabajar con **Spec-Driven Development (SDD)**, la metodología descripta en [specdriven.ai](https://specdriven.ai/), en Claude Code y en claude.ai.

En SDD **la especificación es la fuente de verdad**: primero se acuerda qué se quiere y por qué, después cómo, después las tareas. El código se deriva de eso y se valida contra eso. Estas skills hacen que Claude respete esas etapas, con controles de calidad entre una y otra.

```
sdd/
├── constitution.md     principios permanentes del proyecto
├── README.md           índice: estado y fase de cada especificación
├── plantillas/         specification.md · plan.md · tasks.md
└── specs/NNN-nombre/   specification.md · plan.md · tasks.md
```

## Qué incluye

| Skill | Cómo se usa | Qué hace |
|---|---|---|
| `spec-driven-development` | Se activa sola cuando el proyecto tiene `sdd/` o se habla de especificaciones | El método completo: fases 0 a 6, controles de calidad, reglas, implementación tarea por tarea e iteración |
| `sdd-constitucion` | `/sdd-constitucion` | Etapa 0: construye la constitución por rondas |
| `sdd-especificar` | `/sdd-especificar [NNN o título]` | Etapas 1 y 2: especificación (historias, requisitos, criterios de aceptación) y aclaraciones |
| `sdd-planificar` | `/sdd-planificar [NNN]` | Etapa 3: plan técnico trazable a los requisitos |
| `sdd-tareas` | `/sdd-tareas [NNN]` | Etapa 4: tareas atómicas, ordenadas y verificables |

**Cómo trabajan los comandos por etapa.** Conversan con la persona por rondas de 3 a 5 preguntas, proponen respuestas para que las corrija, actualizan el documento en cada ronda y muestran un **control de madurez**. Solo proponen pasar a la etapa siguiente cuando todos los criterios se cumplen **y la persona lo confirma**. Las decisiones que dependen de otros no se suponen: quedan como aclaraciones.

### Herramienta de validación

`skills/spec-driven-development/scripts/sdd.py` (Python 3.8 o posterior, sin dependencias):

```bash
python sdd.py init --proyecto "Mi proyecto"   # crea sdd/ sin pisar nada existente
python sdd.py nueva "Alta de usuarios"        # crea sdd/specs/NNN-alta-de-usuarios/ y la suma al índice
python sdd.py validar [NNN]                   # controla la calidad; devuelve 1 si hay errores
python sdd.py estado                          # estado, fase y avance de tareas
```

### Tablero de tareas

`skills/spec-driven-development/scripts/tablero.py` (Python 3.8 o posterior, sin dependencias) levanta una web local con las tareas de cada especificación agrupadas por etapa:

```bash
python tablero.py                         # http://127.0.0.1:5070 (solo en el propio equipo)
python tablero.py nota 001 T03 "texto"    # agrega una nota a una tarea
python tablero.py resumen 001             # lo mismo, en texto
```

- **Fuente:** lee los `tasks.md`, que siguen siendo la única fuente; no copia datos.
- **Estado de cada tarea:** lo deduce: hecha, falta revisión, espera a otra persona, bloqueada por otra tarea o pendiente.
- **Actualización:** la página se actualiza sola cuando cambia un archivo.
- **Notas:** se agregan desde la página y quedan en `sdd/tablero/notas.json`.
- **Red:** escucha solo en `127.0.0.1`.

`validar` revisa:
- **Trazabilidad:** cada requisito "Debe" tiene un criterio de aceptación, y los criterios y las tareas apuntan a ids que existen.
- **Criterios de aceptación:** escritos como Dado / Cuando / Entonces.
- **Aclaraciones:** no hay abiertas que bloqueen (formato `Abierta · bloquea RF-NN`) en especificaciones que ya se planificaron.
- **Tareas:** ninguna está marcada como hecha sin decir cómo se verificó.
- **Documentos:** existen el plan y las tareas según la fase.
- **Plantilla:** no quedan restos sin completar.
- **Índice:** coincide con las especificaciones.

## Instalación

### Claude Code
Copiá las carpetas de `skills/` a tu carpeta de skills de usuario. Así quedan disponibles en todos tus proyectos.

```bash
# Linux / macOS
cp -r skills/* ~/.claude/skills/
```
```powershell
# Windows (PowerShell)
Copy-Item skills\* "$env:USERPROFILE\.claude\skills\" -Recurse
```

También se pueden instalar en un solo proyecto, copiándolas a `<proyecto>/.claude/skills/`. En ese caso, cambiá las rutas `~/.claude/skills/spec-driven-development/...` dentro de los cuatro comandos por etapa.

Abrí una sesión nueva de Claude Code para que las tome.

### claude.ai
Subí `dist/spec-driven-development.skill` desde la configuración de skills. Los comandos por etapa (`/sdd-*`) usan campos propios de Claude Code (`disable-model-invocation`, `argument-hint`), así que se usan solo en Claude Code.

## Cómo empezar

1. En un proyecto nuevo: `/sdd-constitucion` (o pedile a Claude "armemos la constitución del proyecto").
2. Por cada funcionalidad: `/sdd-especificar "Título"` → `/sdd-planificar NNN` → `/sdd-tareas NNN`.
3. Implementación: pedile a Claude que implemente la especificación NNN. La skill principal trabaja tarea por tarea, marca `[x]` solo lo verificado y actualiza primero la especificación si aparece algo que no estaba previsto.
4. Corré `sdd.py validar` cuando quieras ver el estado de calidad.

Sugerencia: agregá en el `CLAUDE.md` de tu proyecto una línea que indique leer `sdd/constitution.md` antes de tocar código.

## Créditos
Metodología: [specdriven.ai](https://specdriven.ai/). Estas skills son una implementación independiente.
