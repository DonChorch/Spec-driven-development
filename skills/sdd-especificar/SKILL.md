---
name: sdd-especificar
description: Etapas 1 y 2 de Spec-Driven Development (Especificar y Aclarar). Construye specification.md de una funcionalidad conversando con la persona por rondas, hasta que el qué y el porqué estén maduros y no queden aclaraciones que bloqueen. Se invoca con /sdd-especificar.
disable-model-invocation: true
argument-hint: "[número de especificación existente, o título de una nueva]"
---

# /sdd-especificar · Etapas 1 y 2: Especificar y Aclarar

Vas a definir **qué** se quiere y **por qué**, junto con la persona y por rondas, hasta que la especificación esté madura. En esta etapa no se habla de tecnología: si aparece, anotala para el plan y volvé al qué.

Método general, herramienta y criterios de calidad: `~/.claude/skills/spec-driven-development/SKILL.md`, `scripts/sdd.py` y `references/calidad.md`. Leé la guía de calidad antes de la primera ronda.

## Al empezar
1. **Leé `sdd/constitution.md`.** Su vocabulario y sus principios mandan. Si no existe, sugerí empezar por `/sdd-constitucion` (la persona puede elegir seguir igual).
2. **Elegí la especificación:**
   - Si el argumento es un número, abrí esa.
   - Si es un título, creala con `python ~/.claude/skills/spec-driven-development/scripts/sdd.py nueva "<título>"`.
   - Sin argumento, mostrá `sdd.py estado` y preguntá cuál.
3. **Juntá el contexto que ya existe:** código relacionado, datos, documentos, especificaciones vecinas. Escribí el *Contexto* con la fuente de cada dato.
4. **Mostrá el control de madurez** con lo que ya está cubierto.

## Rondas
En cada ronda:
1. **De 3 a 5 preguntas como máximo**, empezando por lo que más impacta.
   - Primeras rondas: quiénes usan esto, qué problema tienen hoy, qué entra y qué no.
   - Después: requisitos y criterios de aceptación.
   - Al final: aclaraciones.
   - Usá la herramienta de preguntas con opciones cuando sean cerradas.
   - Proponé tus propias respuestas para que la persona corrija.
2. **Actualizá `specification.md` en el momento**, con ids estables (HU-NN, RF-NN, RNF-NN, CA-NN, AC-NN).
3. **Hacé de abogado del diablo:** por cada requisito que escribe, borra o expone datos, preguntá qué pasa si no hay permiso, si no se confirma o si falla un servicio. Ahí salen los criterios negativos.
4. **Detectá las decisiones que no le corresponden a la persona ni a vos** (negocio, institucionales, legales, seguridad, presupuesto) y registralas como aclaraciones, con quién decide. Si impiden diseñar, marcalas "Abierta · bloquea RF-NN".
5. **Corré `sdd.py validar <NNN>`** y mostrá el control actualizado.
6. Actualizá estado y fase: *Borrador · 1* mientras se especifica; *Aclarando · 2* cuando el qué está completo y quedan aclaraciones.

## Control de madurez
| # | Criterio |
|---|---|
| 1 | Resumen sin tecnología, entendible por alguien de negocio |
| 2 | Contexto con datos y su fuente; alcance con "incluye" y "no incluye" |
| 3 | Historias de usuario para cada rol involucrado |
| 4 | Requisitos funcionales atómicos y con prioridad; no funcionales con una medida |
| 5 | Cada RF "Debe" tiene al menos un criterio de aceptación |
| 6 | Cada criterio está escrito como Dado / Cuando / Entonces, dice qué cubre y cómo se verifica; los que escriben o exponen datos tienen su caso negativo |
| 7 | Aclaraciones registradas, con quién decide; **ninguna abierta que bloquee** |
| 8 | Cumplimiento de la constitución revisado, principio por principio |
| 9 | `sdd.py validar <NNN>` sin errores |
| 10 | **La persona confirma que eso es lo que quiere** |

Si el criterio 7 no se cumple porque la decisión depende de otros, **no la supongas**. La especificación queda en *Aclarando* y se lo decís a la persona: qué falta, quién decide y qué parte se puede adelantar.

## Cierre
1. Resumen: una línea por historia, cuántos RF, RNF y CA, y qué aclaraciones se resolvieron y cuáles siguen abiertas.
2. Preguntá: **"¿La especificación está como la querés? ¿Pasamos a diseñar el cómo con /sdd-planificar?"**
3. Con un sí: estado *Planificada* (o se mantiene, si la persona lo prefiere) y fase 3; actualizá el índice (`sdd/README.md`).
4. Sin un sí, o con aclaraciones que bloquean: queda en *Aclarando* y se lista qué falta.
