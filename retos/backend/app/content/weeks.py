"""Contenido de las 12 semanas.

Esto es la **semilla del esqueleto**, no el contenido de producción. Sirve para
que la app funcione de punta a punta y para fijar el formato: cada semana tiene
un tema, tres actividades sin pantalla y tres recompensas digitales a elegir.

El contenido definitivo (redacción, ilustraciones y PDFs imprimibles) se genera
en la fase B. Cuando llegue, sustituye a este fichero sin tocar el motor: la
forma de los datos es la misma.

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

# Cada semana ofrece las mismas tres familias de recompensa. Lo que cambia es
# el asset. Mantener la estructura estable simplifica la pantalla de elección,
# que es la que ve el niño y debe ser siempre igual.
_REWARD_SHAPES = [
    (RewardKind.CHARACTER, "Un amigo nuevo", "Se une a tu cuaderno de aventuras."),
    (RewardKind.STORY, "Un cuento nuevo", "Para leer esta noche."),
    (RewardKind.PRINTABLE, "Una lámina para imprimir", "Se imprime en casa y se colorea."),
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
    rewards = [
        RewardOption(
            option_id=f"w{index:02d}-r{i}",
            kind=kind,
            title=title,
            description=description,
            asset_key=f"w{index:02d}/{kind.value}",
        )
        for i, (kind, title, description) in enumerate(_REWARD_SHAPES, start=1)
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
