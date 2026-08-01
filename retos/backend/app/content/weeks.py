"""Contenido de las 12 semanas.

Cada semana tiene un tema, tres actividades sin pantalla y tres recompensas
digitales entre las que el niño elige una.

Las recompensas son **propias de cada semana**, no plantillas: cada una tiene
su personaje, su cuento y su lámina. Los archivos correspondientes los genera
`retos/studio`, que lee este mismo fichero para que los títulos que sirve la
API y los que aparecen impresos no puedan desincronizarse. `asset_key` es la
ruta del archivo generado, sin extensión.

Reglas al escribir actividades:

- Materiales de andar por casa. Si hace falta comprar algo, la actividad no vale.
- 5 a 15 minutos. Un niño de 3 años no sostiene más.
- Una sola instrucción por actividad, en imperativo y dirigida al adulto.
- Sin cronómetros, sin puntuación, sin comparación con otros niños.
- Nada que prometa un resultado clínico o educativo medible.
"""

from ..models import Activity, AgeBand, RewardKind, RewardOption, SkillArea, WeekTemplate

_RAW: list[dict] = [
    {
        "title": "La semana de las manos",
        "subtitle": "Dedos que aprietan, rasgan y enhebran.",
        "activities": [
            ("Torre de pinzas", "Poned pinzas de la ropa en el borde de un vaso hasta hacer un sol.", SkillArea.MOTRICIDAD_FINA, ["pinzas de la ropa", "un vaso"], 10),
            ("Lluvia de papel", "Rasgad una hoja en trozos pequeños y soltadlos desde arriba.", SkillArea.MOTRICIDAD_FINA, ["papel usado"], 8),
            ("Collar de pasta", "Ensartad macarrones en un cordón para hacer un collar.", SkillArea.MOTRICIDAD_FINA, ["macarrones", "cordón"], 15),
        ],
    },
    {
        "title": "La semana de los colores",
        "subtitle": "Buscar, agrupar y nombrar lo que se ve.",
        "activities": [
            ("Caza del azul", "Recorred la casa y traed cinco cosas azules a la mesa.", SkillArea.ATENCION, [], 10),
            ("Familias de color", "Mezclad la ropa limpia y separadla por colores.", SkillArea.LOGICA, ["ropa limpia"], 12),
            ("El color escondido", "Esconded un objeto y dad pistas solo con colores.", SkillArea.LENGUAJE, [], 10),
        ],
    },
    {
        "title": "La semana de las palabras",
        "subtitle": "Contar, describir y escuchar.",
        "activities": [
            ("¿Qué hay en la bolsa?", "Meted tres objetos en una bolsa; que los describa al tacto.", SkillArea.LENGUAJE, ["una bolsa de tela"], 10),
            ("Cuento al revés", "Contad un cuento conocido cambiando el final.", SkillArea.LENGUAJE, [], 12),
            ("Palabras que empiezan igual", "Buscad tres cosas de la cocina que empiecen por la misma letra.", SkillArea.LENGUAJE, [], 10),
        ],
    },
    {
        "title": "La semana de los tesoros",
        "subtitle": "Ordenar el mundo por tamaños y formas.",
        "activities": [
            ("De pequeño a grande", "Alinead cinco cucharas u objetos del más pequeño al más grande.", SkillArea.LOGICA, ["objetos de casa"], 10),
            ("Mapa del tesoro", "Dibujad un plano sencillo de una habitación y esconded algo.", SkillArea.LOGICA, ["papel", "lápiz"], 15),
            ("Parejas perdidas", "Emparejad calcetines de la colada.", SkillArea.ATENCION, ["calcetines"], 10),
        ],
    },
    {
        "title": "La semana de las emociones",
        "subtitle": "Poner nombre a lo que se siente.",
        "activities": [
            ("Caras de espejo", "Frente al espejo, poned juntos cara de alegría, susto y enfado.", SkillArea.SOCIOEMOCIONAL, ["un espejo"], 8),
            ("El tiempo de hoy", "Que dibuje cómo se ha sentido hoy: sol, nube o tormenta.", SkillArea.SOCIOEMOCIONAL, ["papel", "colores"], 10),
            ("Abrazo de tres", "Pedid tres abrazos distintos: fuerte, corto y de oso.", SkillArea.SOCIOEMOCIONAL, [], 5),
        ],
    },
    {
        "title": "La semana de los números",
        "subtitle": "Contar cosas que se pueden tocar.",
        "activities": [
            ("La mesa de cuatro", "Contad cuántos platos y vasos hacen falta para poner la mesa.", SkillArea.LOGICA, ["vajilla"], 10),
            ("Saltos contados", "Saltad juntos contando en voz alta hasta diez.", SkillArea.LOGICA, [], 8),
            ("Más y menos", "Haced dos montones de garbanzos y decidid cuál tiene más.", SkillArea.LOGICA, ["legumbres secas"], 10),
        ],
    },
    {
        "title": "La semana del cuerpo",
        "subtitle": "Moverse con intención.",
        "activities": [
            ("Circuito de cojines", "Montad un recorrido con cojines para cruzar sin pisar el suelo.", SkillArea.MOTRICIDAD_FINA, ["cojines"], 15),
            ("Estatuas", "Bailad y quedaos quietos cuando pare la música.", SkillArea.ATENCION, ["música"], 10),
            ("El equilibrista", "Caminad sobre una línea de cinta pegada al suelo.", SkillArea.MOTRICIDAD_FINA, ["cinta de carrocero"], 10),
        ],
    },
    {
        "title": "La semana de los sonidos",
        "subtitle": "Escuchar de verdad.",
        "activities": [
            ("Silencio de un minuto", "Sentaos callados un minuto y contad después qué habéis oído.", SkillArea.ATENCION, [], 5),
            ("Orquesta de cocina", "Haced ritmos con dos cacerolas y una cuchara de madera.", SkillArea.ATENCION, ["cacerolas", "cuchara"], 10),
            ("¿Quién hace ese ruido?", "Haced sonidos con objetos y que adivine cuál es con los ojos cerrados.", SkillArea.ATENCION, ["objetos de casa"], 10),
        ],
    },
    {
        "title": "La semana de la cocina",
        "subtitle": "Manos, pasos y paciencia.",
        "activities": [
            ("Batir sin parar", "Que bata huevos o agua con jabón hasta que haga espuma.", SkillArea.MOTRICIDAD_FINA, ["bol", "tenedor"], 10),
            ("La receta de tres pasos", "Preparad una merienda contando en voz alta los tres pasos.", SkillArea.LENGUAJE, ["ingredientes de casa"], 15),
            ("Pelar y contar", "Que pele una mandarina y cuente los gajos.", SkillArea.MOTRICIDAD_FINA, ["una mandarina"], 8),
        ],
    },
    {
        "title": "La semana de la naturaleza",
        "subtitle": "Mirar despacio lo de fuera.",
        "activities": [
            ("Colección de hojas", "Recoged tres hojas distintas en un paseo.", SkillArea.ATENCION, ["una bolsa"], 15),
            ("El árbol de la ventana", "Mirad un árbol y describid tres cosas que hayan cambiado.", SkillArea.LENGUAJE, [], 8),
            ("Piedras ordenadas", "Colocad piedras del paseo de la más lisa a la más rugosa.", SkillArea.LOGICA, ["piedras"], 10),
        ],
    },
    {
        "title": "La semana de las historias",
        "subtitle": "Inventar y recordar.",
        "activities": [
            ("Tres objetos, un cuento", "Coged tres objetos al azar e inventad una historia con ellos.", SkillArea.LENGUAJE, ["objetos de casa"], 12),
            ("El cuento de ayer", "Que os cuente qué hizo ayer, en orden.", SkillArea.LENGUAJE, [], 10),
            ("Dibujar el final", "Que dibuje cómo termina su historia favorita.", SkillArea.LENGUAJE, ["papel", "colores"], 12),
        ],
    },
    {
        "title": "La semana del equipo",
        "subtitle": "Hacer las cosas con otro.",
        "activities": [
            ("Doblar entre dos", "Doblad una sábana entre los dos, sin que toque el suelo.", SkillArea.SOCIOEMOCIONAL, ["una sábana"], 10),
            ("El favor secreto", "Haced juntos algo bueno por alguien de casa sin decírselo.", SkillArea.SOCIOEMOCIONAL, [], 10),
            ("Turnos de verdad", "Jugad a algo donde haya que esperar el turno tres veces.", SkillArea.SOCIOEMOCIONAL, [], 12),
        ],
    },
]

# Las tres familias de recompensa se repiten todas las semanas —personaje,
# cuento y lámina— porque la pantalla de elección la ve un niño de tres años y
# tiene que ser siempre igual. Lo que cambia es el contenido de cada una.
#
# `animal` no lo sirve la API: lo usa el generador de `retos/studio` para saber
# qué dibujar.
_CAST: list[dict] = [
    {
        "animal": "nutria",
        "character": ("Nara la nutria", "Abre todo con las manos. Hasta lo que no debe."),
        "story": ("Las manos de Nara", "Un cuento corto para leer esta noche."),
        "printable": ("Manos para colorear", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "camaleon",
        "character": ("Kimi el camaleón", "Cambia de color según cómo se levante."),
        "story": ("Kimi pierde su color", "Un cuento corto para leer esta noche."),
        "printable": ("Busca y colorea", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "loro",
        "character": ("Pico el loro", "Repite todo lo que oye, y algo más."),
        "story": ("El loro que solo decía sí", "Un cuento corto para leer esta noche."),
        "printable": ("Trazos de palabras", "Se imprime en casa y se repasa con lápiz."),
    },
    {
        "animal": "mapache",
        "character": ("Rufo el mapache", "Guarda tesoros que nadie más ve."),
        "story": ("El tesoro de Rufo", "Un cuento corto para leer esta noche."),
        "printable": ("Recorta tu tesoro", "Se imprime en casa y se recorta."),
    },
    {
        "animal": "oso",
        "character": ("Tila la osa", "Tiene un día distinto cada día."),
        "story": ("El día raro de Tila", "Un cuento corto para leer esta noche."),
        "printable": ("Caras para colorear", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "hormiga",
        "character": ("Uno la hormiga", "Lo cuenta absolutamente todo."),
        "story": ("Uno cuenta hasta diez", "Un cuento corto para leer esta noche."),
        "printable": ("Cuenta y colorea", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "rana",
        "character": ("Brinco la rana", "Salta primero y piensa después."),
        "story": ("Brinco aprende a parar", "Un cuento corto para leer esta noche."),
        "printable": ("Circuito de trazos", "Se imprime en casa y se repasa con lápiz."),
    },
    {
        "animal": "buho",
        "character": ("Ulu el búho", "Oye lo que nadie oye."),
        "story": ("La noche que Ulu escuchó", "Un cuento corto para leer esta noche."),
        "printable": ("Recorta tu orquesta", "Se imprime en casa y se recorta."),
    },
    {
        "animal": "erizo",
        "character": ("Mote el erizo", "Cocina con mucho cuidado. Pincha."),
        "story": ("Mote y la merienda", "Un cuento corto para leer esta noche."),
        "printable": ("Receta para colorear", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "tortuga",
        "character": ("Lenta la tortuga", "Llega la última y se entera de todo."),
        "story": ("El paseo más largo", "Un cuento corto para leer esta noche."),
        "printable": ("Hojas para buscar", "Se imprime en casa y se colorea."),
    },
    {
        "animal": "zorro",
        "character": ("Fábula la zorra", "Nunca cuenta dos veces el mismo cuento."),
        "story": ("La zorra que inventaba", "Un cuento corto para leer esta noche."),
        "printable": ("Dibuja el final", "Se imprime en casa y se dibuja."),
    },
    {
        "animal": "ballena",
        "character": ("Mar la ballena", "Es enorme y aun así necesita ayuda."),
        "story": ("Mar no puede sola", "Un cuento corto para leer esta noche."),
        "printable": ("Recorta y juega en equipo", "Se imprime en casa y se recorta."),
    },
]

_REWARD_ORDER = [
    (RewardKind.CHARACTER, "character"),
    (RewardKind.STORY, "story"),
    (RewardKind.PRINTABLE, "printable"),
]


def _build(index: int, raw: dict) -> WeekTemplate:
    activities = [
        Activity(
            activity_id=f"w{index:02d}-a{i}",
            title=title,
            instructions=instructions,
            skill_area=area,
            materials=materials,
            est_minutes=minutes,
        )
        for i, (title, instructions, area, materials, minutes) in enumerate(raw["activities"], start=1)
    ]
    cast = _CAST[index - 1]
    rewards = [
        RewardOption(
            option_id=f"w{index:02d}-r{i}",
            kind=kind,
            title=cast[key][0],
            description=cast[key][1],
            asset_key=f"w{index:02d}/{kind.value}",
        )
        for i, (kind, key) in enumerate(_REWARD_ORDER, start=1)
    ]
    return WeekTemplate(
        week_index=index,
        title=raw["title"],
        subtitle=raw["subtitle"],
        age_bands=[AgeBand.B3_4, AgeBand.B5_6],
        activities=activities,
        reward_options=rewards,
    )


WEEKS: list[WeekTemplate] = [_build(i, raw) for i, raw in enumerate(_RAW, start=1)]


def total_weeks() -> int:
    return len(WEEKS)


def get_week(week_index: int) -> WeekTemplate | None:
    if 1 <= week_index <= len(WEEKS):
        return WEEKS[week_index - 1]
    return None


def animal_for_week(week_index: int) -> str:
    """Animal protagonista de la semana. Lo consume el generador de assets."""
    return _CAST[week_index - 1]["animal"]
