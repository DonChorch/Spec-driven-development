---
name: sdd-planificar
description: Etapa 3 de Spec-Driven Development (Planificar). Construye plan.md de una especificación aprobada conversando con la persona por rondas, hasta que el diseño técnico esté maduro y sea trazable a todos los requisitos. Se invoca con /sdd-planificar.
disable-model-invocation: true
argument-hint: "[número de especificación]"
---

# /sdd-planificar · Etapa 3: Planificar

Vas a diseñar **cómo** se cumple una especificación ya aprobada, junto con la persona y por rondas. El plan tiene que poder rastrearse hasta los requisitos y apoyarse en el código que ya existe.

Método general, herramienta y criterios de calidad: `~/.claude/skills/spec-driven-development/SKILL.md`, `scripts/sdd.py` y `references/calidad.md`.

## Al empezar
1. **Leé `sdd/constitution.md`** (stack, restricciones, seguridad) y la `specification.md` elegida. Sin argumento, mostrá `sdd.py estado` y preguntá cuál.
2. **Control de entrada:** corré `sdd.py validar <NNN>`. Si hay errores o aclaraciones abiertas que bloquean, **no planifiques**: mostrá qué falta y sugerí volver a `/sdd-especificar`. La persona puede decidir seguir; si lo hace, dejalo escrito en el plan como riesgo.
3. **Explorá el código:** qué existe y se puede reutilizar, qué patrones sigue el proyecto, qué archivos se van a tocar. El plan nombra archivos y funciones reales.
4. **Presentá el enfoque** en un párrafo, con 2 o 3 alternativas y tu recomendación. Es la primera pregunta de la primera ronda.

## Rondas
En cada ronda:
1. **De 3 a 5 preguntas como máximo**, sobre decisiones de diseño que la persona tenga que validar: enfoque, alternativas, modelo de datos, contratos, seguridad, pruebas. Usá la herramienta de preguntas con opciones cuando las decisiones sean cerradas, con tu recomendación primero.
2. **Actualizá `plan.md` en el momento.** En *Componentes y archivos*, la columna *Cubre* tiene los RF y RNF.
3. Si una decisión depende de otros (infraestructura, seguridad, presupuesto, licencias), registrala como **aclaración en la especificación**, no en el plan, y no la supongas.
4. Si aparece algo que la especificación no prevé, **volvé a la especificación primero**: agregá o cambiá el requisito, con el visto bueno de la persona.
5. Mostrá el control actualizado.

## Control de madurez
| # | Criterio |
|---|---|
| 1 | Enfoque elegido y alternativas descartadas, con su motivo |
| 2 | Todo RF y RNF aparece en *Cubre* de algún componente; nada del plan queda sin requisito |
| 3 | Modelo de datos y contratos definidos (entrada, salida, errores, permisos) |
| 4 | Archivos y componentes reales del repositorio, con lo que se reutiliza |
| 5 | Seguridad y privacidad: qué datos, quién accede, qué se registra; consistente con la constitución |
| 6 | Cada criterio de aceptación tiene cómo se va a probar |
| 7 | Riesgos con su mitigación |
| 8 | Ninguna aclaración nueva que bloquee |
| 9 | **La persona aprueba el diseño** |

## Cierre
1. Resumen del plan: enfoque, componentes principales, riesgos y lo que queda abierto.
2. Preguntá: **"¿Aprobás el plan? ¿Pasamos a partirlo en tareas con /sdd-tareas?"**
3. Con un sí: fase 4 en la especificación; actualizá el índice.
4. Sin un sí, queda en fase 3 con la lista de lo pendiente.
