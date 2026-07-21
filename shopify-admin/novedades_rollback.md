# Re-segmentación de "Novedades" — nota de rollback

Colección: Novedades (handle: novedades) — regla smart: TAG == "novedades"

## Problema
1005 de ~1300 productos llevaban el tag `novedades` (lo añade el cron diario a
cada producto nuevo), así que "Novedades" ≈ catálogo entero. Inútil como
escaparate de novedad.

## Acción (2026-07, a petición del usuario, aun a sabiendas de que el cron reañade el tag a productos nuevos)
Se retira el tag `novedades` de los productos creados el 2026-07-14 o antes
(≈726 productos), conservándolo solo en los creados en los últimos 7 días
(created_at > 2026-07-14, ≈279 productos = drop actual).

Distribución en el momento del cambio:
- total tag:novedades = 1005
- creados >2026-07-18 (3d) = 8
- creados >2026-07-14 (7d) = 279  ← se conservan
- creados >2026-07-07 (14d) = 982
- creados >2026-06-21 (30d) = 1005

## Rollback
Reañadir el tag `novedades` a los productos afectados (IDs en
scratchpad/novedades_to_untag.jsonl si se conserva) con productUpdate/tagsAdd.

## Recomendación de mantenimiento (pendiente, estrategia del usuario)
El cron seguirá etiquetando `novedades` los productos nuevos → la colección
volverá a crecer. Para que se mantenga acotada: (a) que el cron retire el tag
del drop anterior al crear uno nuevo, o (b) un trim programado semanal que
deje solo los últimos N días.
