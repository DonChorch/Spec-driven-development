---
name: sdd-tareas
description: Etapa 4 de Spec-Driven Development (Tareas). Parte un plan aprobado en tasks.md, con tareas atómicas, ordenadas, trazables y verificables, conversando con la persona por rondas hasta que la lista esté lista para implementar. Se invoca con /sdd-tareas.
disable-model-invocation: true
argument-hint: "[número de especificación]"
---

# /sdd-tareas · Etapa 4: Tareas

Vas a partir el plan en tareas que se puedan implementar y verificar de a una, junto con la persona y por rondas. Una buena lista de tareas hace que la implementación sea predecible y que el avance sea real, no declarado.

Método general, herramienta y criterios de calidad: `~/.claude/skills/spec-driven-development/SKILL.md`, `scripts/sdd.py` y `references/calidad.md` (sección *Tareas*).

## Al empezar
1. **Leé la especificación y el plan** elegidos. Sin argumento, mostrá `sdd.py estado` y preguntá cuál.
2. **Control de entrada:** debe existir `plan.md` aprobado (fase 3 o más), y `sdd.py validar <NNN>` no tiene que dar errores. Si no se cumple, mostrá qué falta y sugerí `/sdd-planificar`.
3. **Proponé una primera versión** de `tasks.md`, derivada del plan: una tarea por cambio revisable, con *Depende de*, *Cubre* y *Verificación* prevista. Mostrala como tabla y abrí la primera ronda.

## Rondas
En cada ronda:
1. **De 3 a 5 preguntas como máximo**:
   - ¿El orden es el correcto?
   - ¿Hay tareas que partir o que juntar?
   - ¿Hay verificaciones que no se pueden hacer (falta un entorno, permisos, datos) y que haya que planear?
   - ¿Qué va primero por riesgo?
   - ¿Qué hace la persona y qué hacés vos (por ejemplo, scripts que ejecuta un DBA)?
2. **Actualizá `tasks.md` en el momento.**
3. **Corré `sdd.py validar <NNN>`** y mostrá el control actualizado.

## Control de madurez
| # | Criterio |
|---|---|
| 1 | Cada tarea es atómica (cabe en un cambio revisable; sin "y") |
| 2 | Dependencias explícitas y orden posible sin ciclos |
| 3 | Cada tarea dice qué cubre (RF, RNF o CA existentes) |
| 4 | Cada tarea dice cómo se va a verificar |
| 5 | Todo criterio de aceptación tiene al menos una tarea que lo verifica |
| 6 | Lo que no puede hacer el agente (ejecutar en producción, aprobar, decidir) está asignado a quien corresponde |
| 7 | Las primeras tareas reducen el mayor riesgo |
| 8 | `sdd.py validar <NNN>` sin errores |
| 9 | **La persona aprueba la lista** |

## Cierre
1. Resumen: cantidad de tareas, orden de las primeras y verificaciones que dependen de otros.
2. Preguntá: **"¿Aprobás las tareas? ¿Empiezo a implementar por T01?"**
3. Con un sí: estado *En curso* y fase 5; actualizá el índice. La implementación sigue las reglas de la skill `spec-driven-development` (fase 5): una tarea por vez, `[x]` solo verificada, y la especificación primero si aparece algo nuevo.
4. Sin un sí, queda en fase 4 con lo pendiente.
