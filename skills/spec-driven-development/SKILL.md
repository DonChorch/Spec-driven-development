---
name: spec-driven-development
description: Desarrollo guiado por especificaciones (Spec-Driven Development, metodología de specdriven.ai) con constitution.md, specification.md, plan.md y tasks.md, en fases (Constitución, Especificar, Aclarar, Planificar, Tareas, Implementar, Iterar) y con controles de calidad para avanzar. Usala siempre que el proyecto tenga una carpeta sdd/ o especificaciones, y cuando la persona pida armar o seguir specs, una constitución, requisitos, criterios de aceptación, un plan técnico o tareas; cuando quiera arrancar una funcionalidad nueva "bien hecha" antes de programar; cuando pregunte en qué estado está una especificación o qué falta; o cuando diga "spec", "SDD", "spec-driven", "especificación", "historia de usuario" o "trazabilidad", aunque no nombre la metodología. También antes de implementar algo grande en un proyecto que ya trabaja con specs.
---

# Spec-Driven Development

En SDD **la especificación es la fuente de verdad**. El trabajo de la persona y tuyo es dejar claro qué se quiere y por qué; el código se deriva de eso y se valida contra eso. Escribir código rápido sin una especificación aprobada parece eficiente, pero produce lo que nadie pidió y pierde las decisiones que no te correspondían. Por eso esta skill pone controles entre las fases.

## Estructura

```
sdd/
├── constitution.md     principios permanentes (los cumple todo lo demás)
├── README.md           índice: una fila por especificación con estado y fase
├── plantillas/         specification.md · plan.md · tasks.md
└── specs/NNN-nombre/   specification.md · plan.md · tasks.md
```

Las plantillas genéricas están en `assets/plantillas/`. Si el proyecto tiene `sdd/plantillas/`, usá esas: pueden estar adaptadas al proyecto.

## Herramienta

`scripts/sdd.py` (Python 3, sin dependencias). Ejecutala desde la raíz del proyecto, o con `--raiz`:

| Comando | Para qué |
|---|---|
| `python <skill>/scripts/sdd.py init --proyecto "Nombre"` | Crea `sdd/` (no pisa nada existente) |
| `python <skill>/scripts/sdd.py nueva "Título"` | Crea `specs/NNN-titulo/` con el número siguiente y la suma al índice |
| `python <skill>/scripts/sdd.py validar [NNN]` | Control de calidad: trazabilidad, Dado/Cuando/Entonces, aclaraciones que bloquean, tareas sin verificar, índice. Devuelve 1 si hay errores |
| `python <skill>/scripts/sdd.py estado` | Estado, fase y avance de tareas de cada especificación |

Corré `validar` **antes de anunciar** que una especificación avanzó de fase, y al terminar una implementación. Los errores se corrigen; los avisos se revisan y se explican.

## Comandos interactivos por etapa

Para trabajar una etapa conversando por rondas hasta que esté madura, la persona puede usar:

| Comando | Etapa | Produce |
|---|---|---|
| `/sdd-constitucion` | 0 | `constitution.md` |
| `/sdd-especificar [NNN o título]` | 1 y 2 | `specification.md` con aclaraciones |
| `/sdd-planificar [NNN]` | 3 | `plan.md` |
| `/sdd-tareas [NNN]` | 4 | `tasks.md` |

Cada uno tiene su control de madurez y **solo propone pasar a la siguiente etapa cuando todos los criterios se cumplen y la persona lo confirma**. Si la persona pide trabajar una etapa sin el comando, seguí el mismo estilo: rondas cortas, el documento actualizado en cada ronda y el control a la vista.

## Cómo arrancar en cada pedido

1. **Ubicá el proyecto.** Si existe `sdd/`, leé `constitution.md` y el `README.md` antes de proponer nada. La constitución define vocabulario, principios y reglas que tenés que respetar. Si no existe y la persona quiere trabajar así, ofrecé `init`.
2. **Identificá qué te piden** y en qué fase está esa especificación. Se puede dar a pedido o en orden, pero sin saltear controles.
3. **Decí en una línea en qué fase vas a trabajar** y qué vas a producir.

## Fases y controles para avanzar

Cada fase tiene un control de salida. **No pases a la siguiente sin cumplirlo.** Si la persona pide saltearlo, explicá en una oración qué se pierde y respetá su decisión dejándola escrita en la especificación.

### 0 · Constitución
- Principios **verificables**, con su porqué; glosario de términos propios; stack; reglas de seguridad y datos; cómo se modifica.
- Partí de lo que ya sabés del proyecto (código, documentos, conversación). Lo que no sabés va como pregunta, no como suposición.
- **Control:** la persona la aprueba. Versión y fecha.

### 1 · Especificar (qué y por qué)
- Completá `specification.md`: resumen sin tecnología, contexto con datos y su fuente, alcance (incluye y no incluye), historias de usuario, requisitos funcionales (RF-NN, con prioridad Debe, Debería o Podría), no funcionales medibles (RNF-NN) y criterios de aceptación (CA-NN).
- **Control:** cada RF "Debe" tiene al menos un CA. Cada CA está escrito como Dado/Cuando/Entonces, dice qué cubre y cómo se verifica. Para el detalle y ejemplos, leé `references/calidad.md`.

### 2 · Aclarar
- Buscá ambigüedades y, sobre todo, **decisiones que no te corresponden**: de negocio, institucionales, de seguridad, legales, de presupuesto o de licencias. Registralas en *Aclaraciones*, con quién decide.
- Marcá "Abierta · bloquea RF-NN" lo que impide planificar.
- Revisá la constitución principio por principio y completá *Cumplimiento de la constitución*.
- **Control:** ninguna aclaración abierta que bloquee. Preguntale a la persona las que pueda responder; las demás quedan abiertas y la especificación queda en *Aclarando*.

### 3 · Planificar (cómo)
- `plan.md`: enfoque y alternativas descartadas con su motivo, arquitectura, modelo de datos, contratos, componentes y archivos (columna *Cubre*), seguridad, pruebas y riesgos.
- Buscá en el código lo que ya existe y reutilizalo: el plan nombra archivos y funciones reales.
- **Control:** todo RF y RNF aparece en el plan; nada del plan queda sin un requisito que lo justifique.

### 4 · Tareas
- `tasks.md`: tareas atómicas, ordenadas por dependencia, cada una con *Cubre* y *Verificación*.
- **Control:** todo CA tiene al menos una tarea que lo verifica. `validar` sin errores.

### 5 · Implementar
- Una tarea por vez, en orden. Antes de empezar, releé los requisitos y criterios que cubre.
- Marcá `[x]` **solo cuando la verificaste**, y escribí cómo. Si no pudiste probarla (falta un entorno, una clave, un permiso), dejala `[x]` solo si el código está completo, y decilo en la verificación.
- Si aparece algo que la especificación no prevé, **pará y actualizá primero la especificación** (o registrá una aclaración). El código nunca se aparta de la especificación en silencio.
- **Control:** CA cumplidos y verificados; `validar` sin errores; estado *Implementada*.

### 6 · Iterar
- Lo aprendido (errores de campo, mediciones, decisiones nuevas) vuelve a la especificación como nueva revisión: fecha, qué cambió y por qué.
- Actualizá el índice.

## Reglas que hacen sólida la metodología

- **Sin especificación aprobada no hay implementación.** Para un cambio chico (un error, una línea), alcanza una tarea en la especificación existente; no hace falta una nueva.
- **No supongas decisiones de otros.** Horarios, plazos de retención, qué datos salen a un tercero, quién tiene un rol, umbrales, licencias pagas: van a *Aclaraciones*. Podés proponer una respuesta, marcada como propuesta.
- **Verificación honesta.** No digas "funciona" sin haberlo probado. Separá lo verificado de lo que no pudiste verificar.
- **Trazabilidad completa:** RF → CA → tarea → código y prueba. Si algo no se puede rastrear, sobra o falta.
- **Respetá el vocabulario de la constitución.** Si define términos, usalos exactamente.
- **El índice siempre al día:** estado y fase de cada especificación en `sdd/README.md`.
- **Documentar lo ya construido:** si el código existe antes que la especificación, escribila tal como está (estado *Implementada*, tareas marcadas con su verificación real) y anotá lo que falta. No inventes verificaciones que no ocurrieron.

## Cómo reportar

Al terminar, en pocas líneas:
- Qué especificación, en qué fase quedó y con qué estado.
- Qué produjiste.
- El resultado de `validar`.
- Las aclaraciones abiertas que necesitan una respuesta de la persona, empezando por las que bloquean.
- La recomendación del siguiente paso.

Hablá en el idioma y el tono del proyecto; si la constitución lo define, seguilo.
