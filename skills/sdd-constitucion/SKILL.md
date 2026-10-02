---
name: sdd-constitucion
description: Etapa 0 de Spec-Driven Development. Construye o revisa sdd/constitution.md conversando con la persona por rondas, hasta que el documento esté maduro. Se invoca con /sdd-constitucion.
disable-model-invocation: true
argument-hint: "[nombre del proyecto o tema a revisar]"
---

# /sdd-constitucion · Etapa 0: Constitución

Vas a construir (o revisar) la constitución **junto con la persona**, por rondas, hasta que esté madura. No la escribas entera de una vez desde tus supuestos: una constitución que la persona no discutió no la va a respetar nadie.

Método general, herramienta y criterios de calidad: `~/.claude/skills/spec-driven-development/SKILL.md`, `scripts/sdd.py` y `references/calidad.md`. Leelos al empezar.

## Al empezar
1. **Buscá `sdd/`.** Si no existe, corré `python ~/.claude/skills/spec-driven-development/scripts/sdd.py init --proyecto "<nombre>"`. Si existe `sdd/constitution.md`, leela: vas a revisarla, no a reemplazarla.
2. **Juntá lo que ya se sabe** antes de preguntar: README, código, documentos, la conversación. Así no le preguntás a la persona cosas que están escritas.
3. **Mostrá el control de madurez** (abajo), con lo que ya está cubierto.

## Rondas
En cada ronda:
1. Hacé **de 3 a 5 preguntas como máximo**, de la parte menos madura. Si las opciones son cerradas, usá la herramienta de preguntas con opciones. Proponé una respuesta cuando puedas ("propongo X porque Y, ¿va?"): es más fácil corregir que inventar.
2. Con las respuestas, **actualizá `sdd/constitution.md` en el momento**, para que el avance no se pierda.
3. **Mostrá el control actualizado**: cada criterio con ✅ o ⬜ y, si falta, qué falta.
4. Si todos los criterios están cumplidos, pasá al *Cierre*. Si no, otra ronda.

La persona puede cortar cuando quiera: guardá lo que haya, marcá el estado "borrador" y decí qué quedó pendiente.

## Control de madurez
| # | Criterio |
|---|---|
| 1 | Propósito: para qué existe y para quién, en tres oraciones como máximo |
| 2 | Glosario con los términos propios del dominio, y qué no confundir |
| 3 | Al menos 3 principios **verificables**, cada uno con su porqué |
| 4 | Reglas de seguridad y datos: secretos, datos personales, qué nunca se hace sin una persona |
| 5 | Regla de verificación (cómo se prueba y qué se dice cuando algo no se pudo probar) |
| 6 | Stack y restricciones técnicas (red, licencias, distribución) |
| 7 | Gobierno: cómo se cambia, quién aprueba, versión y fecha |
| 8 | Sin contradicciones entre principios, ni con lo que ya existe en el código |
| 9 | **La persona aprueba el documento** |

Un principio es verificable si se puede responder "¿esta especificación o este cambio lo cumple?" con sí o no. "Código de calidad" no lo es; "toda tarea dice cómo se verificó" sí.

## Cierre
1. Mostrá un resumen de la constitución en 5 a 8 líneas.
2. Preguntá explícitamente: **"¿La aprobás y pasamos a especificar la primera funcionalidad con /sdd-especificar?"**
3. Solo con un sí: cambiá el estado a "vigente", actualizá la versión y la fecha, y recomendá el siguiente paso.
4. Sin aprobación, la constitución queda en borrador y no se avanza.
