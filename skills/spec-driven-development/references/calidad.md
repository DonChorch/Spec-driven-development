# Guía de calidad de las especificaciones

Leé esta guía cuando escribas o revises requisitos, criterios de aceptación, aclaraciones o tareas.

## Contenido
1. Requisitos
2. Criterios de aceptación
3. Aclaraciones
4. Plan
5. Tareas
6. Revisión contra la constitución
7. Señales de una especificación débil

## 1. Requisitos

Un requisito dice **qué** tiene que pasar, no **cómo** se construye.

| Débil | Mejor | Por qué |
|---|---|---|
| "El sistema debe ser rápido" | RNF-01: la búsqueda responde en menos de 2 s en el 90 % de los casos | Se puede medir |
| "Usar Redis para el caché" | RF-04: el listado de productos se puede servir con hasta 60 s de antigüedad | La tecnología va en el plan |
| "Mejorar la seguridad" | RF-02: un vendedor solo puede ver los pedidos de sus propios clientes | Se puede verificar con una prueba de permisos |

- **Prioridad:** Debe (sin esto no sirve), Debería (importante, se puede postergar con un motivo), Podría (deseable).
- **Un requisito, una idea.** Si dice "y", probablemente son dos.

## 2. Criterios de aceptación

Formato: **Dado** (situación de partida) **Cuando** (acción) **Entonces** (resultado observable). Cada uno cubre uno o más requisitos y dice cómo se verifica.

| Débil | Mejor |
|---|---|
| "El pago funciona bien" | **Dado** un carrito con 2 productos **cuando** pago con una tarjeta rechazada **entonces** el pedido queda "pago pendiente", no se descuenta stock y se muestra el motivo del rechazo |
| "No se pueden ver datos ajenos" | **Dado** un vendedor A **cuando** pide el pedido de un cliente del vendedor B **entonces** recibe "no encontrado" y el intento queda registrado |

- **El "Entonces" se observa desde afuera:** un archivo, una respuesta, una fila, un mensaje. "Se procesa correctamente" no sirve.
- **Incluí el caso negativo** de todo lo que escribe, borra o expone datos: qué pasa si no se confirma, si no tiene permiso, si el servicio está caído.
- **Verificación:** nombre de la prueba automática, "prueba manual: pasos…" o "revisión de X". Si todavía no se puede verificar, escribí **Pendiente** y el motivo.

## 3. Aclaraciones

Una aclaración es una pregunta que **no le corresponde contestar al agente**: decisiones de negocio, institucionales, de seguridad, de presupuesto, o datos que nadie te dio.

- Registrá quién decide, aunque sea "a definir".
- Marcá **"Abierta · bloquea RF-NN"** cuando impida diseñar ese requisito. Con aclaraciones que bloquean no se pasa a *Planificar*.
- Si proponés una respuesta, escribila como **propuesta**, no como decisión.
- Una aclaración resuelta deja la decisión escrita, con quién la tomó y cuándo.

**Ejemplos de lo que nunca se supone:** horarios de atención, plazos de retención de datos, qué datos pueden salir a un servicio externo, quién tiene un rol, umbrales de un SLA, licencias con costo.

## 4. Plan

- Cada componente o archivo dice qué requisitos cubre (columna *Cubre*).
- Las alternativas descartadas llevan su motivo: evitan que la discusión vuelva.
- Lo que el plan no puede resolver por falta de una decisión vuelve a *Aclaraciones*.

## 5. Tareas

- **Atómica:** cabe en un cambio revisable. Si tiene "y", partila.
- **Ordenada:** columna *Depende de*.
- **Trazable:** columna *Cubre*, con RF, RNF o CA existentes.
- **Verificable:** la columna *Verificación* dice cómo se comprobó (prueba, comando, captura, revisión).
- **Honesta:** `[x]` solo si se verificó. Si se hizo sin poder probarla, puede quedar `[x]`, pero la verificación lo dice ("compila; sin probar en el equipo real").

## 6. Revisión contra la constitución

Antes de pasar de fase, recorré cada principio de `constitution.md` y marcá en la especificación `[x]` (cumple), `[~]` (parcial, con el motivo) o `[ ]` (no aplica o pendiente). Una contradicción no se resuelve en silencio: o cambia la especificación, o se propone un cambio a la constitución (nueva versión, motivo y aprobación).

## 7. Señales de una especificación débil

- El resumen menciona tecnologías.
- Requisitos que no se pueden medir.
- Criterios de aceptación sin caso negativo.
- Ninguna aclaración en un tema que obviamente depende de otros.
- Un plan que agrega funciones que nadie pidió.
- Tareas marcadas sin verificación.
- Código ya escrito que no aparece en ninguna tarea.
