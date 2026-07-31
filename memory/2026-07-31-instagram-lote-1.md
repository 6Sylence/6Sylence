# Lote 1 de Instagram — publicado

**31/07/2026, 07:47–07:49 UTC** · cuenta `@streetroyaltyhood` (SRHOOD Street Royalty Hood)
· vía Postiz, publicación inmediata (`type: "now"`).

Las 10 publicaciones figuran como `PUBLISHED` en Postiz. Verificado a posteriori con
`GET /public/v1/posts?startDate=…&endDate=…`, no solo por el 200 del envío.

## Canales de Postiz

| id | plataforma | perfil |
|---|---|---|
| `cms8mkzd00eqbqn0y0v23rn7l` | instagram | SRHOOD Street Royalty Hood |
| `cms8mlo1r0eqjqn0yck149p8s` | facebook | Street Royalty Hood |

## Orden publicado (= orden de cuadrícula, se lee de abajo a arriba)

1. SEDA REAL · 2. VICTORIA REAL · 3. HIERRO Y ORO · 4. PIEDRA REAL · 5. INTARSIA REAL
· 6. CIFRA REAL · 7. EL REMATE · 8. ORO EN LA GRIETA · 9. DOS CARAS · 10. LA CORONA NO SE PIDE

La numeración del JSON (`n`) es la del documento de textos, no la de publicación: el orden
del fichero está pensado para que la cuadrícula alterne calzado / prenda / accesorio.

## Decisiones de esta tanda

- **Hashtags en el pie**, no en primer comentario. `FEED-10-TEXTOS.md` proponía el comentario;
  el script lo soporta con `--hashtags-en-comentario`, pero no se usó. Para el lote 2 conviene
  decidirlo antes: mezclar los dos formatos en la misma cuenta no aporta nada.
- **Pausa de 15 s** entre envíos. El límite de Instagram es 50 publicaciones/24 h, así que
  10 de golpe no lo roza; la pausa es por el límite por hora de Postiz.
- **JPEG q92, subsampling 0**. La API de Instagram rechaza PNG: los `.png` originales están en
  `out/`, los enviados en `out/jpg/` (ignorado por git).

## Pendiente en la app

**Texto alternativo.** Postiz no lo transmite (la API de Meta lo admite desde marzo de 2025,
pero Postiz no expone el campo). Hay que pegarlo a mano en cada publicación:
`···` → Editar → Editar texto alternativo. Los diez textos están en `postiz_posts.json`,
campo `alt`, y los imprime el script al terminar.

## Clave

`POSTIZ_API_KEY` viaja por entorno; el fichero de trabajo vive fuera del repositorio
(`$SCRATCHPAD/.postiz_key`, 600). **No se guarda en el repositorio ni en GitHub.**
La clave actual se transmitió en claro en una conversación: conviene rotarla en Postiz
(Settings → Public API) y volver a inyectarla como variable de entorno.
