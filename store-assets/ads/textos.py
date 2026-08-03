#!/usr/bin/env python3
"""
Motor de textos del lote: pies, hashtags y texto alternativo.

Principio: **nada se inventa**. El cuerpo del pie sale de la descripción real del
producto en la tienda —el patrón que lleva estampado y su ficha técnica—, así que
lo que promete el anuncio es exactamente lo que llega a casa. Lo único escrito a
mano es el gancho de cada cápsula, que es donde vive la voz de marca.

Reglas heredadas del lote 1 y que siguen vigentes:
  · Ningún reclamo de envío. El umbral de 39 € no se anuncia.
  · BIENVENIDA15 solo como 15% de primera compra, y solo en la pieza de marca.
  · Precio real, tomado de la variante.
  · La primera línea es lo único visible antes del «…más»: ahí va el gancho.
"""
import re, html

# ── ganchos por cápsula ───────────────────────────────────────────────────────
# Varios por cápsula: con 4-5 piezas de la misma familia en el lote, un solo
# gancho repetido convierte la cuadrícula en un copia-pega.
CAPSULAS = {
    "meandro-real": dict(
        linea="CÁPSULA MEANDRO · LABERINTO REAL",
        ganchos=["La greca griega lleva tres mil años sin pasar de moda.",
                 "Un laberinto no es un lío. Es un camino con una sola salida.",
                 "El meandro se dibujó primero en las ánforas. Luego en todo lo demás.",
                 "Empieza en una esquina y no se acaba nunca."],
        tags=["meandro", "grecagriega"]),
    "intarsia": dict(
        linea="CÁPSULA MARQUETERÍA · INTARSIA REAL",
        ganchos=["Suelo de palacio. Suela de calle.",
                 "La taracea es carpintería de precisión disfrazada de dibujo.",
                 "Nogal, arce y palo rosa. Cortados a la medida de una prenda.",
                 "El mismo oficio de los parqués reales, en formato urbano."],
        tags=["marqueteria", "intarsia"]),
    "brocado-real": dict(
        linea="CÁPSULA BROCADO · ORO SOBRE ESMERALDA",
        ganchos=["El brocado vestía palacios. Ahora pisa aceras.",
                 "Oro sobre verde noche, de borde a borde.",
                 "La seda que solo tocaba la corte, en tejido de diario.",
                 "Medallones de oro y una corona repetida hasta el infinito."],
        tags=["brocado", "damasco"]),
    "malaquita-real": dict(
        linea="CÁPSULA MALAQUITA · ESMERALDA Y ORO",
        ganchos=["La malaquita fue piedra de reyes mucho antes de ser nuestra.",
                 "Verde con vetas de oro: eso es una piedra, no un color.",
                 "Se pule hasta que el mineral parece un mapa.",
                 "La corona, esta vez, es mineral."],
        tags=["malaquita", "esmeralda"]),
    "forja-real": dict(
        linea="CÁPSULA FORJA · CELOSÍA DE HERRERÍA",
        ganchos=["Mira los portales de tu barrio. El diseño ya estaba ahí.",
                 "La reja que separa la calle del patio, convertida en prenda.",
                 "Volutas de hierro y remaches de oro, de punta a punta.",
                 "Hierro forjado: lo más duro del edificio y lo más decorado."],
        tags=["forja", "hierroforjado"]),
    "eslabon-real": dict(
        linea="CÁPSULA ESLABÓN · CADENA REAL",
        ganchos=["Una cadena de oro no se lleva. Se hereda.",
                 "Eslabones en diagonal, de borde a borde, y coronas escondidas.",
                 "Lo que sujeta también decora.",
                 "La cadena más vista del barrio, dibujada en el tejido."],
        tags=["cadena", "eslabon"]),
    "camo-real": dict(
        linea="CÁPSULA CAMO · CAMUFLAJE CORONADO",
        ganchos=["El camuflaje se inventó para no ser visto. Este no.",
                 "Manchas de camuflaje con coronas dentro. Busca bien.",
                 "Militar de origen, urbano de destino.",
                 "Camo real: el que se pone cuando no piensa esconderse."],
        tags=["camo", "camuflaje"]),
    "baraja-real": dict(
        linea="CÁPSULA BARAJA · REY DE PICAS",
        ganchos=["La corte entera cabe en una baraja.",
                 "Rey de picas: la carta que no se descarta.",
                 "Naipes, coronas y escaleras reales.",
                 "En la baraja también hay realeza, y es la única que se reparte."],
        tags=["baraja", "naipes"]),
    "plumaje-real": dict(
        linea="CÁPSULA PLUMAJE · ABANICO REAL",
        ganchos=["El pavo real no presume. Solo se da la vuelta.",
                 "Plumas abiertas en abanico sobre negro de noche.",
                 "Hay animales que nacen con el traje puesto.",
                 "Un abanico de plumas es una corona horizontal."],
        tags=["plumaje", "pavoreal"]),
    "guilloche-real": dict(
        linea="CÁPSULA GUILLOCHÉ · GRABADO DE SEGURIDAD",
        ganchos=["El grabado de los billetes existe para que no se puedan copiar.",
                 "Guilloché: líneas que se cruzan sin tocarse nunca.",
                 "El dibujo que llevan los billetes y los relojes buenos.",
                 "Se llama guilloché y es antifalsificación hecha ornamento."],
        tags=["guilloche", "grabado"]),
    "neon-real": dict(
        linea="CÁPSULA NEÓN · NOCHE ELÉCTRICA",
        ganchos=["La ciudad de noche no está apagada. Está en otro turno.",
                 "Neón: el único letrero que se lee desde la otra acera.",
                 "24/7, como el rótulo que nunca cierra.",
                 "Luz de gas encerrada en un tubo. Lleva un siglo ganando."],
        tags=["neon", "nocheurbana"]),
    "vidriera-real": dict(
        linea="CÁPSULA VIDRIERA · LUZ DE CATEDRAL",
        ganchos=["Una vidriera es un muro que deja pasar la luz de colores.",
                 "Rosetón: la rueda de cristal más ambiciosa jamás construida.",
                 "Plomo y vidrio. Ochocientos años y sigue impresionando.",
                 "La catedral entera se sostiene para enmarcar esa ventana."],
        tags=["vidriera", "roseton"]),
    "corona-boreal": dict(
        linea="CÁPSULA CORONA BOREAL · CARTA CELESTE",
        ganchos=["Corona Borealis existe. Está sobre tu cabeza ahora mismo.",
                 "Hay una corona en el cielo y nadie la reclama.",
                 "Cartas celestes, astrolabios y meridianos.",
                 "Navegar era mirar arriba y creerse el mapa."],
        tags=["cartaceleste", "astronomia"]),
    "frecuencia": dict(
        linea="CÁPSULA FRECUENCIA · LA SEÑAL",
        ganchos=["Una onda cruzando el pecho de lado a lado.",
                 "Frecuencia: lo que suena aunque no se vea.",
                 "La señal no se interrumpe. Solo cambia de canal.",
                 "Sube el volumen hasta que se vea."],
        tags=["frecuencia", "sonido"]),
    "tartan-real": dict(
        linea="CÁPSULA TARTÁN · HERENCIA REAL",
        ganchos=["Cada tartán identificaba un clan. Este identifica el tuyo.",
                 "Cuadros de las Tierras Altas en clave urbana.",
                 "El tartán fue prohibido por ley. Por eso sigue aquí.",
                 "Un tejido puede ser un apellido."],
        tags=["tartan", "cuadros"]),
    "kintsugi-real": dict(
        linea="CÁPSULA KINTSUGI · LA LUNA ROTA",
        ganchos=["En Japón reparan la cerámica rota con oro.",
                 "No esconden la grieta: la coronan.",
                 "Lo que se rompió y volvió a unirse vale más.",
                 "Kintsugi: quinientos años diciendo lo mismo."],
        tags=["kintsugi", "japon"]),
    "nube-imperial": dict(
        linea="CÁPSULA NUBE IMPERIAL · CIELO DE CORTE",
        ganchos=["Las nubes de los mantos imperiales no son nubes. Son rango.",
                 "Cielo de corte: volutas de nube sobre navy profundo.",
                 "En la corte china, la nube era un símbolo de suerte.",
                 "Nubes bordadas para gente que no mira al suelo."],
        tags=["nubeimperial", "orientaldesign"]),
    "suminagashi": dict(
        linea="CÁPSULA SUMINAGASHI · TINTA FLOTANTE",
        ganchos=["Suminagashi: tinta sobre agua, mil doscientos años haciéndolo.",
                 "El dibujo lo hace la corriente, no la mano.",
                 "Cada remolino sale distinto porque el agua nunca repite.",
                 "Marmoleado japonés, el arte de soltar el control."],
        tags=["suminagashi", "marmoleado"]),
    "azulejo-real": dict(
        linea="CÁPSULA AZULEJO · CERÁMICA REAL",
        ganchos=["El azulejo no es decoración. Es la fachada entera.",
                 "Cobalto sobre blanco: el color que puso de moda un imperio.",
                 "Estrella de ocho puntas, la geometría que no se cansa.",
                 "Cerámica de patio andaluz, a escala de prenda."],
        tags=["azulejo", "ceramica"]),
    "nomada-real": dict(
        linea="CÁPSULA NÓMADA · PATRONES DE RUTA",
        ganchos=["Los tejidos nómadas viajaban más que quien los llevaba.",
                 "Ikat, bogolán, pantera: patrones que cruzaron continentes.",
                 "Nada de esto se diseñó en una oficina.",
                 "Patrones de ruta: los que se llevan puestos al moverse."],
        tags=["ikat", "bogolan"]),
    "telar-real": dict(
        linea="CÁPSULA TELAR · TRAMA REAL",
        ganchos=["Todo tejido es una decisión repetida diez mil veces.",
                 "Asanoha, seigaiha, bargello: tres telares, un mismo oficio.",
                 "La trama es lo que no se ve y lo sostiene todo.",
                 "Un patrón de telar es matemática con las manos."],
        tags=["telar", "trama"]),
    "paisley-real": dict(
        linea="CÁPSULA PAÑUELO · PAISLEY REAL",
        ganchos=["El paisley viene de Persia y se quedó en la calle.",
                 "Boteh: la gota curvada que lleva mil años sin cambiar.",
                 "El estampado del pañuelo de siempre, en talla completa.",
                 "Cachemir: el dibujo que sobrevivió a todas las modas."],
        tags=["paisley", "cachemir"]),
    "laurel-real": dict(
        linea="CÁPSULA LAUREL · LA CORONA LAUREADA",
        ganchos=["El laurel no se compra. Se gana.",
                 "Coronaba a los que volvían habiendo ganado algo.",
                 "Nosotros solo lo bordamos. Lo otro es cosa tuya.",
                 "Victoria real: la corona más antigua que existe."],
        tags=["laurel", "victoria"]),
    "relieve-real": dict(
        linea="CÁPSULA RELIEVE · TOPOGRAFÍA REAL",
        ganchos=["Un mapa de curvas de nivel es un paisaje visto desde arriba.",
                 "Equidistancia 50 m; actitud a nivel del asfalto.",
                 "La montaña dibujada como la dibujan los que la suben.",
                 "Cotas, curvas y rosa de los vientos."],
        tags=["topografia", "mapas"]),
    "cifra-real": dict(
        linea="CIFRA REAL · EL MONOGRAMA DE LA CASA",
        ganchos=["Una cifra es el monograma con el que firma la realeza.",
                 "La SR coronada y ceñida en laurel. Sin más.",
                 "Quien la reconoce, la reconoce.",
                 "La firma de la casa, en pequeño y en su sitio."],
        tags=["monograma", "minimalstreetwear"]),
}

# cápsula por defecto para las piezas sin etiqueta de cápsula
BASE = dict(linea="ROYALTY CLASSICS · LA CORONA",
            ganchos=["La corona no se pide. Se lleva.",
                     "Lo básico bien hecho también es una declaración.",
                     "Una pieza lisa aguanta más temporadas que diez estampadas.",
                     "El fondo de armario de la casa.",
                     "Sin estampado que lo salve: aquí manda el corte.",
                     "Lo que te pones cuando no quieres pensar qué ponerte.",
                     "La pieza que no caduca en marzo."],
            tags=["basicos", "royaltyclassics"])

# Ganchos por tipo, para las piezas sin cápsula. Los básicos son 189 de golpe y no
# tienen historia de cápsula que contar; con solo los siete de BASE, la primera
# línea —lo único que se ve antes del «…más»— se repetiría cada siete publicaciones
# y el perfil entero olería a plantilla.
GANCHOS_TIPO = {
    "Hoodie": ["Una sudadera buena se nota en el segundo invierno, no en el primero.",
               "Capucha que se sostiene sola. Ese es el detalle.",
               "El gramaje se paga una vez y se agradece cada día.",
               "La prenda que más se lleva y la que peor se suele elegir."],
    "Cropped Hoodie": ["Corta arriba, ancha de hombro: el corte hace el fit.",
                       "Cropped sin quedarte corta de tejido.",
                       "El mismo gramaje que la larga, con otra silueta.",
                       "Sube el bajo y cambia el conjunto entero."],
    "Sudadera": ["Cuello redondo, sin capucha, sin ruido.",
                 "La sudadera de toda la vida, hecha como se hacía.",
                 "Felpa por dentro y caída recta por fuera.",
                 "Menos prenda, más tejido."],
    "Sudadera Cremallera": ["Abierta es una capa; cerrada es un abrigo.",
                            "La cremallera te da dos prendas por el precio de una.",
                            "Entretiempo resuelto.",
                            "Se abre, se cierra, y el fit cambia."],
    "Camiseta": ["Una camiseta lisa es la prueba del algodón.",
                 "Si el cuello aguanta, la camiseta es buena.",
                 "Corte recto, hombro en su sitio, sin sorpresas.",
                 "La pieza que más lavas: elige bien."],
    "Camiseta Manga Larga": ["Manga larga: media estación entera resuelta.",
                             "Debajo o sola. Las dos funcionan.",
                             "Puños que no se abren a la tercera semana.",
                             "La capa que no abulta."],
    "Camiseta de Tirantes": ["Sisa amplia y caída limpia. Verano.",
                             "Para entrenar o para el bar. Lo mismo da.",
                             "Menos tela, mismo corte.",
                             "Julio en Madrid pide esto."],
    "Polo": ["El polo vuelve, y vuelve sin logo enorme.",
             "Cuello con estructura: ahí está la diferencia.",
             "Formal por arriba, calle por abajo.",
             "Punto fino, corte recto."],
    "Gorra": ["Una gorra bien bordada dura más que la moda que la trajo.",
              "Visera plana o curva: la discusión eterna.",
              "El bordado en relieve no se despega al tercer lavado.",
              "Lo primero que se ve de ti a diez metros."],
    "Gorro": ["Punto grueso: el invierno se nota en el gramaje.",
              "La vuelta ajustable es lo que separa un gorro bueno de uno que baila.",
              "Se dobla, se guarda en el bolsillo, no se deforma.",
              "Frío de verdad, gorro de verdad."],
    "Bucket Hat": ["Ala media: sombra sin parecer un pescador.",
                   "El bucket volvió y no se ha ido.",
                   "Estructura en el ala para que no se venza.",
                   "Sol de agosto, cabeza cubierta."],
    "Bandana": ["Al cuello, en la muñeca o asomando del bolsillo.",
                "Lo más barato de la casa y lo que más cambia un look.",
                "Un cuadrado de tela con más usos de los que crees.",
                "El remate que nadie espera."],
    "Jogger": ["Puño en el tobillo: lo que separa un jogger de un chándal.",
               "Felpa francesa por dentro, calle por fuera.",
               "Bolsillos que aguantan un móvil sin deformarse.",
               "Cómodo no tiene por qué significar dejado."],
    "Pantalón": ["Corte recto, tejido con cuerpo.",
                 "El pantalón que aguanta el día entero.",
                 "Ni pitillo ni saco: en su sitio.",
                 "Lo de abajo también cuenta."],
    "Shorts": ["Largo por encima de la rodilla, ni un dedo más.",
               "Verano sin renunciar al corte.",
               "Cintura elástica que no marca.",
               "Cuarenta grados y aun así con criterio."],
    "Chaqueta": ["Bomber: la chaqueta que nunca se equivoca.",
                 "Puños acanalados y cierre limpio.",
                 "Capa exterior sin volumen.",
                 "La que te pones encima de todo lo demás."],
    "Cortavientos": ["El viento se para con tejido, no con capas.",
                     "Se pliega, cabe en la mochila, y salva la tarde.",
                     "Ligero por fuera, seco por dentro.",
                     "Para cuando el día cambia de idea."],
    "Zapatillas": ["Suela vulcanizada: la construcción que aguanta.",
                   "Lona y goma. Lleva un siglo funcionando.",
                   "Se ensucian, se lavan, siguen.",
                   "El calzado que combina con todo lo que ya tienes."],
    "ZAPATILLAS": ["Suela vulcanizada: la construcción que aguanta.",
                   "Caña alta, ojales metálicos, cordones que no se deshilachan.",
                   "Lona y goma. Lleva un siglo funcionando.",
                   "Se ensucian, se lavan, siguen."],
    "Riñonera": ["Lo esencial, cruzado al pecho.",
                 "Cabe lo que necesitas y nada de lo que no.",
                 "Correa ajustable, cremallera que cierra de verdad.",
                 "Las manos libres cambian cómo andas."],
    "Mochila": ["Lo que te llevas encima todos los días merece estar bien hecho.",
                "Bolsillo acolchado dentro, tejido resistente fuera.",
                "Capacidad de día entero.",
                "La mochila se elige una vez cada muchos años."],
    "Bolsa": ["Tote de tejido resistente, no de papel.",
              "Asas reforzadas: ahí es donde revientan todas.",
              "Cabe la compra, el portátil o las dos cosas.",
              "La bolsa que dejas de perder."],
    "Calcetines": ["El detalle que solo se ve cuando te sientas.",
                   "Caña media, elástico que no aprieta.",
                   "Lo último que se elige y lo primero que se nota.",
                   "Pie negro, tejido transpirable."],
}

# ── hashtags por tipo de pieza ────────────────────────────────────────────────
BASE_TAGS = ["srhood", "streetroyalty", "streetwearespaña", "modaurbanaespaña"]
TAGS_TIPO = {
    "ZAPATILLAS": ["zapatillasaltas", "sneakerheadspain", "calzadostreetwear", "sneakers"],
    "Zapatillas": ["zapatillasaltas", "sneakerheadspain", "calzadostreetwear", "sneakers"],
    "Hoodie": ["sudaderas", "hoodiestyle", "outfitdeldia", "ropaurbana"],
    "Cropped Hoodie": ["sudaderas", "hoodiestyle", "modamujer", "outfitdeldia"],
    "Sudadera": ["sudaderas", "outfitdeldia", "modahombre", "modamujer"],
    "Sudadera Cremallera": ["sudaderas", "hoodiestyle", "outfitdeldia", "ropaurbana"],
    "Camiseta": ["camisetas", "oversized", "outfitdeldia", "ropaurbana"],
    "Camiseta Manga Larga": ["camisetas", "mangalarga", "outfitdeldia", "ropaurbana"],
    "Camiseta de Tirantes": ["camisetas", "tirantes", "outfitdeldia", "streetstyle"],
    "Bandana": ["bandana", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Bucket Hat": ["buckethat", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Riñonera": ["rinonera", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Mochila": ["mochila", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Gorra": ["gorra", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Gorro": ["beanie", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Calcetines": ["calcetines", "accesoriosurbanos", "completaellook", "streetstyle"],
    "Chaqueta": ["chaqueta", "outfitdeldia", "modahombre", "ropaurbana"],
    "Cortavientos": ["cortavientos", "outfitdeldia", "streetstyle", "ropaurbana"],
    "Jogger": ["joggers", "outfitdeldia", "streetstyle", "ropaurbana"],
    "Pantalón": ["pantalones", "outfitdeldia", "streetstyle", "ropaurbana"],
    "Shorts": ["shorts", "outfitdeldia", "streetstyle", "ropaurbana"],
    "Polo": ["polo", "outfitdeldia", "modahombre", "ropaurbana"],
    "Bolsa": ["totebag", "accesoriosurbanos", "completaellook", "streetstyle"],
}
CIERRE_TAGS = ["edicionlimitada", "hechobajodemanda", "diseñoespañol", "marcaespañola"]

# nombre neutro de la prenda para el texto alternativo.
# El tipo de Shopify no distingue altas de slip-on ni de deportivas —las tres son
# "ZAPATILLAS"—, así que el corte se lee del título, que sí lo dice.
PRENDA_TITULO = [
    ("Zapatillas Altas", "Zapatillas altas de lona"),
    ("Zapatillas Slip-On", "Zapatillas slip-on de lona"),
    ("Zapatillas Deportivas", "Zapatillas deportivas"),
    ("Zapatillas Lona", "Zapatillas de lona"),
    ("Camiseta Manga Larga", "Camiseta de manga larga"),
    ("Camiseta de Tirantes", "Camiseta de tirantes"),
    ("Sudadera Cremallera", "Sudadera con capucha y cremallera"),
    ("Hoodie Cremallera", "Sudadera con capucha y cremallera"),
    ("Cropped Hoodie", "Sudadera corta con capucha"),
    ("Quarter Zip", "Sudadera de media cremallera"),
    ("Bucket Hat", "Gorro bucket"),
]
PRENDA = {
    "ZAPATILLAS": "Zapatillas de lona", "Zapatillas": "Zapatillas de lona",
    "Hoodie": "Sudadera con capucha", "Cropped Hoodie": "Sudadera corta con capucha",
    "Sudadera": "Sudadera de cuello redondo",
    "Sudadera Cremallera": "Sudadera con capucha y cremallera",
    "Camiseta": "Camiseta de manga corta",
    "Camiseta Manga Larga": "Camiseta de manga larga",
    "Camiseta de Tirantes": "Camiseta de tirantes",
    "Bandana": "Bandana cuadrada", "Bucket Hat": "Gorro bucket",
    "Riñonera": "Riñonera", "Mochila": "Mochila", "Gorra": "Gorra",
    "Gorro": "Gorro de punto", "Calcetines": "Calcetines",
    "Chaqueta": "Chaqueta bomber", "Cortavientos": "Cortavientos",
    "Jogger": "Pantalón jogger", "Pantalón": "Pantalón", "Shorts": "Pantalón corto",
    "Polo": "Polo", "Bolsa": "Bolsa de tela",
}

# frases de la ficha técnica que NO deben acabar en el pie: logística, tallaje y
# el bloque de referencia de proveedor (Gildan 18600, Lane Seven LS14014…), que es
# información de almacén, no de escaparate.
RUIDO = re.compile(r"(tabla de tallas|talla[s]?\s*:|talla\s|ancho pecho|equivalencia|"
                   r"selector|env[ií]o|gratis|si dudas|elige una talla|us\s+eu|cm\)|"
                   r"producci[óo]n\s*:|t[ée]cnica\s*:|color\s*:|"
                   r"producci[óo]n bajo demanda|se imprime al hacer|"
                   r"\b[A-Z][a-z]+\s+[A-Z]{1,3}\d{4,})", re.I)


# ── titulares de plancha ──────────────────────────────────────────────────────
# El titular sale del propio nombre del producto, que ya está bien puesto
# («Puerta del Reino», «Astrolabio del Norte»). Solo se escribe a mano cuando el
# derivado se repetiría en la cuadrícula —cinco planchas diciendo ESSENTIAL— o
# cuando el nombre no deja nada al quitarle la prenda y el color.
PREFIJOS = ["Hoodie Premium", "Hoodie Cremallera", "Relax Hoodie", "Zip Hoodie",
            "Cropped Hoodie", "Hoodie", "Zapatillas Altas", "Zapatillas Slip-On",
            "Zapatillas Deportivas", "Zapatillas Lona", "Zapatillas",
            "Sudadera Cremallera", "Sudadera", "Camiseta Manga Larga",
            "Camiseta de Tirantes", "Camiseta", "Bandana", "Bucket Hat", "Riñonera",
            "Mochila", "Quarter Zip", "Polo", "Jogger", "Gorra", "Gorro",
            # nombres de los básicos, que repiten la prenda dentro del propio título
            "Sweatpants Heavyweight", "Sweatpants", "Cortavientos", "Chaqueta Bomber",
            "Bomber", "Mesh Shorts", "Shorts", "Pantalón", "Bolsa de Tela", "Bolsa",
            "Tote", "Pullover", "Calcetines"]

# marca al principio del título: no aporta nada en una plancha que ya lleva la
# corona y «STREET ROYALTY HOOD» en la cabecera
MARCA = re.compile(r"^(street royalty(\s*\|)?|srhood)\s*", re.I)

TITULOS = {
    # las cinco Essential solo se distinguían por el color
    "zapatillas-altas-essential-hombre-crema": "MARFIL",
    "zapatillas-altas-essential-hombre-negro": "NEGRO ABSOLUTO",
    "zapatillas-altas-essential-hombre-verde-oliva": "VERDE CUARTEL",
    "zapatillas-altas-essential-mujer-arena": "DUNA REAL",
    "zapatillas-altas-essential-mujer-burdeos": "BURDEOS REAL",
    # tartán: seis piezas, un solo nombre
    "zapatillas-altas-tartan-hombre-burdeos": "TARTÁN REAL",
    "sudadera-tartan-real-granate": "CLAN PROPIO",
    "zapatillas-lona-tartan-real-mujer-negro": "HERENCIA",
    "zapatillas-lona-tartan-real-hombre-negro": "TIERRAS ALTAS",
    "mochila-tartan-real-burdeos": "EQUIPAJE REAL",
    "camiseta-manga-larga-tartan-negro": "BANDA DE GALA",
    "bucket-hat-nube-imperial-reversible-navy-marfil": "CIELO DE CORTE",
    "hoodie-nube-imperial-navy": "NUBE IMPERIAL",
    "zapatillas-altas-nube-imperial-hombre-navy": "ANDAR EN NUBES",
    "hoodie-premium-camo-real-navy": "CAMO REAL",
    "bandana-camo-real-verde": "VERDE DE GUARDIA",
    "camiseta-camo-real-verde-militar": "NO SE ESCONDE",
    "hoodie-frecuencia-navy": "FRECUENCIA",
    "sudadera-cremallera-frecuencia-negro": "SEÑAL PARTIDA",
    "bandana-frecuencia-negro": "ONDA CORTA",
    "street-royalty-hoodie-premium-arena-crown-capsule": "CORONA CLARA",
    "street-royalty-hoodie-premium-navy-crown-capsule": "CORONA DE NOCHE",
    "street-royalty-hoodie-premium-negro-crown-capsule": "CORONA MACIZA",
    # sin nombre propio: se lo damos
    "srhood-hoodie-premium-cotton-heritage-street-royalty": "LA BASE",
    "srhood-relax-hoodie-as-colour-street-royalty": "SIN PRISA",
    "srhood-quarter-zip-premium-negro-street-royalty": "MEDIO CIERRE",
    "zapatillas-altas-meandro-hombre-negro-crema": "MEANDRO REAL",
    "zapatillas-slip-on-meandro-mujer-crema-terracota": "EL LABERINTO",
    "zapatillas-altas-eslabon-hombre-negro": "CADENA REAL",
    "sudadera-cremallera-eslabon-negro": "ESLABÓN",
    "sudadera-marqueteria-real-negro": "TARACEA",
    "camiseta-marqueteria-real-negro": "MARQUETERÍA",
    "bandana-marqueteria-nogal": "NOGAL Y ARCE",
    "camiseta-meandro-real-negro": "GRECA REAL",
    "rinonera-forja-negro-oro": "TRAS LA REJA",
    "camiseta-de-tirantes-forja-negro": "FORJA REAL",
    "zapatillas-altas-rex-mujer-negro": "REINA REX",
    "zapatillas-altas-rex-hombre-negro": "REX",
    "zapatillas-lona-moire-mujer-blanco-negro": "MOIRÉ",
    "zapatillas-lona-moire-hombre-blanco-negro": "AGUAS DE SEDA",
    "street-royalty-zapatillas-de-lona-crown-hombre-black-edition": "CORONA DE LONA",
    "street-royalty-zapatillas-altas-crown-mujer-black-edition": "CORONA PROPIA",
    "street-royalty-zapatillas-altas-crown-black-edition": "CROWN",
    "sudadera-guilloche-cinta-grabada-negro": "CINTA GRABADA",
}


def titular(handle, titulo):
    if handle in TITULOS:
        return TITULOS[handle]
    base = MARCA.sub("", titulo.split(" — ")[0]).strip()
    for p in sorted(PREFIJOS, key=len, reverse=True):
        if base.lower().startswith(p.lower()):
            base = base[len(p):].strip()
            break
    base = re.sub(r"\b(Hombre|Mujer|AS Colour|Cotton Heritage|Stella Nora|Reversible)\b",
                  "", base)
    return re.sub(r"\s+", " ", base).strip(" —-").upper()


def _limpio(body_html):
    s = re.sub(r"<[^>]+>", " ", body_html or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def _may(t):
    """Mayúscula inicial sin tocar el resto: las descripciones empiezan en minúscula
    porque en la ficha van detrás de dos puntos."""
    return t[0].upper() + t[1:] if t else t


def _cortar(t, n):
    """Recorta por palabra entera: un alt cortado a media palabra se lee fatal en
    un lector de pantalla."""
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0]


def prenda(prod, tipo):
    for clave, nombre in PRENDA_TITULO:
        if clave.lower() in prod["title"].lower():
            return nombre
    return PRENDA.get(tipo, "Prenda")


def frases(body_html, n=2):
    """Las primeras frases útiles de la descripción: el patrón y la ficha.

    Las fichas de la tienda siguen el patrón «<prenda> de la Cápsula X — Y : <lo que
    se ve>». La entradilla sobra en el pie —la cápsula ya va en la plancha—, así que
    se corta por los dos puntos y se conserva lo de después, que es la descripción
    visual. Luego se tira la logística: tallas, equivalencias US/EU y cualquier
    mención de envío, que además no puede salir por política.
    """
    s = _limpio(body_html)
    s = re.split(r"Tabla de tallas|Medidas de la prenda", s)[0]
    cab = re.match(r"^.{0,120}?\s:\s+(.+)$", s, re.S)   # entradilla «… : …»
    if cab:
        s = cab.group(1)
    trozos = [t.strip(" ·—-:") for t in re.split(r"(?<=\.)\s+|\s+·\s+", s) if t.strip()]
    buenas = [t for t in trozos if len(t) > 28 and not RUIDO.search(t)]
    return buenas[:n]


def pie(prod, cap, idx, tipo=None):
    """gancho · qué es · ficha · cierre. En ese orden, siempre.

    Con cápsula, el gancho lo pone la cápsula: es la historia que se está contando.
    Sin cápsula, lo pone el tipo de prenda —hablar de la capucha en una gorra no dice
    nada—, y solo si el tipo no está en la tabla se cae a los genéricos de BASE.
    """
    if cap in CAPSULAS:
        pool = CAPSULAS[cap]["ganchos"]
    else:
        pool = GANCHOS_TIPO.get(tipo) or BASE["ganchos"]
    c = CAPSULAS.get(cap, BASE)
    gancho = pool[idx % len(pool)]
    cuerpo = frases(prod.get("body_html"), 2)
    partes = [gancho]
    for t in cuerpo:
        partes.append(_may(t.rstrip(".")) + ".")
    partes.append("Serie limitada, hecha bajo demanda. Link en bio.")
    return "\n\n".join(partes)


def hashtags(tipo, cap, idx, titulo=""):
    c = CAPSULAS.get(cap, BASE)
    tipo_tags = list(TAGS_TIPO.get(tipo, ["ropaurbana", "streetstyle"])[:3])
    # no etiquetar como "altas" unas slip-on o unas deportivas
    if "zapatillasaltas" in tipo_tags and "altas" not in titulo.lower():
        tipo_tags[tipo_tags.index("zapatillasaltas")] = "zapatillas"
    t = BASE_TAGS + tipo_tags + c["tags"] + [CIERRE_TAGS[idx % len(CIERRE_TAGS)]]
    vistos, out = set(), []
    for x in t:
        if x not in vistos:
            vistos.add(x)
            out.append("#" + x)
    return " ".join(out[:11])


def alt(prod, tipo, cap, titulo):
    """Descripción de accesibilidad: qué se ve, no qué se vende.

    Meta la usa además para clasificar la imagen, así que lleva la prenda, el color,
    el patrón y la marca — en ese orden, que es el que aporta.
    """
    nombre = prenda(prod, tipo)
    color = prod["title"].split(" — ")[-1] if " — " in prod["title"] else ""
    cand = frases(prod.get("body_html"), 1)
    patron = _cortar((cand[0] if cand else titulo).strip(), 170).rstrip(" ,.;:—-")
    frase = nombre + (f" en {color.lower()}" if color else "")
    if patron:
        frase += ". " + _may(patron)
    if cap in CAPSULAS:
        nom = CAPSULAS[cap]["linea"].split("·")[0].replace("CÁPSULA", "").strip().title()
        firma = f"Cápsula {nom} de SRHOOD, streetwear español."
    else:
        firma = "SRHOOD, streetwear español hecho bajo demanda."
    return f"{frase}. {firma}"
