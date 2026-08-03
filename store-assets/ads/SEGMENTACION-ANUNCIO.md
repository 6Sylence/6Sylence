# Segmentación del anuncio de tocados — configuración lista para pegar

Cuenta publicitaria: **1349746030685206** (Street Royalty Hood).
Creatividades: `out/anuncios/srhood-anuncio-tocados-{verano|invierno}-{story|feed}.jpg`.

**No he podido crearlo en la cuenta desde aquí**: Adspirer está a 15/15 llamadas del
plan gratuito y no repone hasta el **8 de agosto**, y no hay token de Meta en el
entorno. Todo lo de abajo son los valores exactos, campo por campo, en el orden en
que aparecen en el administrador.

> **Créalo en pausa.** Revisa el píxel antes de que gaste un euro (ver el último
> apartado). Un anuncio que corre sin `AddToCart` funcionando es dinero tirado que
> además no deja aprendizaje.

---

## 0 · La decisión que va antes de la segmentación: qué pieza enseñas

El primer montaje tenía de protagonista un **gorro de punto acrílico**. Estamos en
agosto. Ningún ajuste de público arregla enseñar un gorro de invierno a alguien que
está a 35 grados: pagas alcance por una pieza que no se va a comprar, y el píxel
aprende de un fracaso.

- **Ahora → juego `verano`**: dos buckets y una gorra. Desde 26,95 €.
- **A partir de mediados de octubre → juego `invierno`**: entra el gorro de punto.
  Desde 24,95 €.

El precio de la plancha se calcula de las piezas que salen en ella, así que al
cambiar de juego no se queda un «desde 24,95 €» falso.

---

## 1 · Campaña

| Campo | Valor |
|---|---|
| Nombre | `SRHOOD · Tocados · Prospección · Ago-26` |
| Objetivo | **Ventas** |
| Presupuesto | A nivel de **conjunto de anuncios**, no de campaña (con un solo conjunto, el CBO no aporta y quita control) |
| Categoría especial | Ninguna |
| Prueba A/B | Desactivada |

## 2 · Conjunto de anuncios

| Campo | Valor |
|---|---|
| Nombre | `Amplio · ES 20-34 · AddToCart` |
| Conversión | Sitio web |
| Píxel | El de srhood.com |
| **Evento** | **Añadir al carrito** |
| Presupuesto | **20 €/día** (ver por qué abajo) |
| Calendario | Sin fecha de fin |

### Público

| Campo | Valor |
|---|---|
| **Ubicación** | España — **excluye Canarias, Ceuta y Melilla** (IGIC y aduana se comen el pedido) |
| **Edad** | 20 – 34 |
| **Género** | Todos |
| **Idioma** | Español |
| **Segmentación detallada** | Vacía. Sí: **vacía** |
| **Público ampliado (Advantage+)** | Activado |
| **Exclusiones** | Ninguna todavía — no hay público que excluir |

**Por qué el detalle va vacío.** Con un pedido en el histórico, el píxel no sabe nada.
Encerrarlo en una lista de intereses le quita el único margen que tiene para
encontrar al comprador por su cuenta, y encima con un presupuesto que no da para
llenar un público estrecho. El público amplio con Advantage+ es lo que mejor funciona
en cuentas nuevas de comercio electrónico, y no es intuición: es que el algoritmo
necesita espacio para explorar antes de que tú le digas dónde mirar.

**Los intereses tienen su momento, y no es este.** Cuando lleves ~50 `AddToCart`
acumulados, abre un segundo conjunto con esta pila y compáralo contra el amplio:

> Carhartt WIP · Stüssy · Vans · Converse · Dickies · New Era · JD Sports · Snipes ·
> Kaotiko · Grimey Wear · tatuaje ornamental · arte japonés · Hypebeast ·
> Highsnobiety · comportamiento «Compradores comprometidos»

### Ubicaciones

| Campo | Valor |
|---|---|
| Tipo | **Advantage+ (automáticas)** |
| Excluir | **Audience Network** y **vídeo con recompensa** |

El resto se deja. Audience Network fuera por una razón concreta y no por manía:
en fase de recogida de datos te llena el píxel de clics accidentales de juegos, y un
píxel entrenado con basura tarda semanas en desintoxicarse.

### Atribución

7 días de clic, 1 día de visualización (el valor por defecto). No lo toques hasta
tener volumen.

## 3 · Anuncio

| Campo | Valor |
|---|---|
| Nombre | `Tocados verano · LO PRIMERO QUE SE VE` |
| Identidad | Cuenta de Instagram `@streetroyaltyhood` + página de Facebook |
| Formato | Imagen única |
| Contenido | `...-verano-feed.jpg` (4:5) y `...-verano-story.jpg` (9:16) — sube las dos y asigna cada una a su ubicación |
| Texto principal | Ver `ANUNCIO-GORROS.md`, versión A para empezar |
| Titular | `Buckets y gorras · desde 26,95 €` |
| **Llamada a la acción** | **Comprar** |
| **URL** | `https://srhood.com/collections/gorras-gorros` |
| Parámetros | `utm_source=meta&utm_medium=paid&utm_campaign=tocados_ago26&utm_content={{ad.name}}` |

---

## 4 · Por qué 20 €/día y un solo conjunto

Meta necesita del orden de **50 eventos de optimización por conjunto y semana** para
salir de la fase de aprendizaje. Con un `AddToCart` costando entre 1,50 € y 4 € en
ropa en España, 50 a la semana son 75-200 € semanales: **entre 11 y 28 €/día**. Veinte
está dentro.

De ahí sale la consecuencia incómoda: **partir el presupuesto en dos conjuntos deja
los dos sin salir de aprendizaje**, y un conjunto en aprendizaje permanente entrega
peor y más caro. Con menos de 40 €/día, uno solo. Corregí aquí lo que te dije antes
de mirar los números de la cuenta.

Con 20 €/día y un CPM español de 3-6 € para este público, salen unas 4.000
impresiones diarias. Las dos primeras semanas estás **comprando datos, no ventas**;
juzgar el anuncio antes de eso es juzgar ruido.

## 5 · Lo que hay que verificar antes de gastar

1. **El píxel dispara `AddToCart`.** Administrador de eventos → Probar eventos →
   añade algo al carrito en srhood.com y comprueba que llega. Si no llega, todo lo
   anterior es decorativo: el conjunto optimiza a un evento que no existe.
2. **La API de Conversiones está activa** con deduplicación por `event_id`. Sin ella
   pierdes entre el 20% y el 40% de las señales en iOS.
3. **El catálogo está sincronizado** con Meta, para poder usar Advantage+ Catálogo
   cuando haya datos.
4. **Las 115 fichas que aún prometen «envío gratis desde 50 €»**. Mandar tráfico
   pagado a una página que promete algo que el checkout no cumple es la forma más
   cara que hay de perder un carrito.

## 6 · Cuándo cambiar algo

| Señal | Qué hacer |
|---|---|
| ~50 `AddToCart` acumulados | Abre el conjunto de intereses y compáralo contra el amplio |
| ~50 compras al mes | Cambia el evento de optimización a **Compra** |
| ~1.000 visitantes en 30 días | Monta el retargeting a 7 días, ahí sí optimizando a Compra y con `BIENVENIDA15` |
| ~100 compradores | Ya hay semilla para un público similar (1%) |
| Ticket medio < 39 € al mes | El problema no es el anuncio: el catálogo de entrada es demasiado barato para el coste de envío |

---

## Anexo · Carga para la API de Marketing

Para cuando haya acceso —el 8 de agosto con Adspirer, o antes con un token—. Los
`interests` van por nombre: sus identificadores hay que resolverlos contra
`/search?type=adinterest` porque cambian entre cuentas y mercados.

```json
{
  "campaign": {
    "name": "SRHOOD · Tocados · Prospección · Ago-26",
    "objective": "OUTCOME_SALES",
    "special_ad_categories": [],
    "status": "PAUSED"
  },
  "adset": {
    "name": "Amplio · ES 20-34 · AddToCart",
    "daily_budget": 2000,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "ADD_TO_CART",
    "destination_type": "WEBSITE",
    "attribution_spec": [{"event_type": "CLICK_THROUGH", "window_days": 7},
                         {"event_type": "VIEW_THROUGH", "window_days": 1}],
    "targeting": {
      "geo_locations": {"countries": ["ES"]},
      "excluded_geo_locations": {"regions": [
        {"name": "Canarias"}, {"name": "Ceuta"}, {"name": "Melilla"}]},
      "age_min": 20,
      "age_max": 34,
      "genders": [1, 2],
      "locales": [6],
      "targeting_automation": {"advantage_audience": 1},
      "exclusions": {},
      "excluded_publisher_categories": [],
      "publisher_platforms": ["facebook", "instagram", "messenger"],
      "targeting_relaxation_types": {"lookalike": 1, "custom_audience": 1}
    },
    "status": "PAUSED"
  },
  "creative": {
    "name": "Tocados verano · LO PRIMERO QUE SE VE",
    "object_story_spec": {
      "link_data": {
        "link": "https://srhood.com/collections/gorras-gorros",
        "message": "Lo primero que se ve de ti a diez metros.\n\nBuckets de ala media y gorras con la corona bordada en relieve. Talla única, bordado denso que no se despega al tercer lavado.\n\nCada pieza se fabrica cuando la pides.",
        "name": "Buckets y gorras · desde 26,95 €",
        "description": "Producción bajo demanda",
        "call_to_action": {"type": "SHOP_NOW"}
      }
    }
  }
}
```

`locales: [6]` es español. `genders: [1, 2]` es ambos —omitirlo hace lo mismo, pero
dejarlo explícito evita que alguien lo cambie por accidente creyendo que estaba sin
configurar.
