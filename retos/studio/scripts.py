"""Guiones: el texto de los cuentos y la especificación de cada lámina.

Vive aquí y no en el backend a propósito. La API solo necesita saber que
existe un cuento y cómo se llama; el texto completo es material de imprenta y
no tiene por qué viajar por la red.

Cómo están escritos los cuentos:

- Tres páginas. Una o dos frases por página. Se leen en voz alta en un minuto.
- Frases cortas y vocabulario de andar por casa.
- El personaje falla antes de conseguirlo. Nunca gana a la primera.
- El final premia el intento, no el resultado. Es lo contrario de lo que hace
  la mecánica de recompensas, y por eso hace falta: el cuento equilibra al
  premio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sheet:
    """Qué se imprime esta semana y qué hay que hacer con ello."""

    kind: str  # colorear | buscar | trazos | recortar | dibujar
    instruction: str  # una línea, dirigida al adulto
    prompt: str = ""  # texto grande dentro de la lámina, si lo lleva


@dataclass(frozen=True)
class Script:
    pages: tuple[str, str, str]
    sheet: Sheet


SCRIPTS: dict[int, Script] = {
    1: Script(
        pages=(
            "Nara tenía dos manos y mil ideas. Abría cajas, nudos y hasta el bote de la miel.",
            "Un día encontró una caja cerrada con siete lazos. Probó con los dientes y no salió.",
            "Entonces usó los dedos, despacio, uno a uno. Dentro no había nada, y Nara se rio: "
            "lo bueno había sido abrirla.",
        ),
        sheet=Sheet("colorear", "Colorea a Nara. Sin prisa y sin salirse... o saliéndose."),
    ),
    2: Script(
        pages=(
            "Kimi cambiaba de color sin querer. Verde en la hoja, gris en la piedra.",
            "Una mañana se despertó blanco del todo. Buscó su color por todo el jardín.",
            "Lo encontró al reírse: se puso naranja entero. Su color no estaba fuera, estaba dentro.",
        ),
        sheet=Sheet("buscar", "Colorea solo las hojas. Las demás formas se quedan en blanco."),
    ),
    3: Script(
        pages=(
            "Pico repetía todo. Si oía «sí», decía «sí». Si oía «patata», decía «patata».",
            "Un día le preguntaron: «¿y tú qué quieres?». Pico abrió el pico y no salió nada.",
            "Lo pensó un rato largo. Luego dijo: «quiero contar algo mío». Y lo contó.",
        ),
        sheet=Sheet("trazos", "Repasa los caminos con el dedo primero y con lápiz después."),
    ),
    4: Script(
        pages=(
            "Rufo guardaba tesoros: un botón, una llave, media concha.",
            "Su bolsa se llenó tanto que ya no podía cargarla.",
            "Ordenó todo de pequeño a grande y regaló la mitad. La bolsa pesaba menos y él sonreía más.",
        ),
        sheet=Sheet("recortar", "Recorta por la línea de puntos. Guarda tus tesoros en una caja."),
    ),
    5: Script(
        pages=(
            "Tila se levantó y no sabía cómo estaba. Ni contenta ni triste.",
            "Su madre le preguntó: «¿qué tiempo hace hoy dentro de ti?».",
            "Tila lo pensó. «Nublado», dijo. Y al decirlo, salió un poco de sol.",
        ),
        sheet=Sheet("colorear", "Colorea a Tila. Mientras, contadle cómo os habéis sentido hoy."),
    ),
    6: Script(
        pages=(
            "Uno contaba todo: las hojas, las patas, las gotas.",
            "Un día llegó a diez y se quedó parada. Después del diez no sabía qué venía.",
            "Su amiga le dijo: «once». Uno dio un salto: siempre hay un número más.",
        ),
        sheet=Sheet("buscar", "Cuenta en voz alta y colorea tantas formas como años tiene."),
    ),
    7: Script(
        pages=(
            "Brinco saltaba antes de mirar. Saltaba y luego pensaba.",
            "Una tarde saltó a un charco que no era charco: era barro hasta arriba.",
            "Ahora cuenta hasta tres antes de saltar. Salta igual de lejos, pero cae donde quiere.",
        ),
        sheet=Sheet("trazos", "Recorre el circuito con el dedo. Después, con lápiz y sin parar."),
    ),
    8: Script(
        pages=(
            "Ulu oía todo: el viento, una hoja, una miga cayendo.",
            "Pero había tanto ruido dentro de su cabeza que no oía nada.",
            "Cerró los ojos y se quedó quieto un minuto. Entonces sí: oyó el río, muy lejos.",
        ),
        sheet=Sheet("recortar", "Recorta los instrumentos y montad una orquesta en la mesa."),
    ),
    9: Script(
        pages=(
            "Mote quería hacer la merienda solo. Tenía púas, no dedos largos.",
            "Rompió dos huevos fuera del bol y tiró la harina al suelo.",
            "A la tercera le salió. Estaba torcida y era la mejor merienda del mundo.",
        ),
        sheet=Sheet("colorear", "Colorea la merienda de Mote y luego preparad una de verdad."),
    ),
    10: Script(
        pages=(
            "Todos llegaban antes que Lenta. Siempre.",
            "Un día contaron lo que habían visto por el camino y casi nadie recordaba nada.",
            "Lenta habló de tres hojas, dos piedras y un caracol. Había hecho el paseo más largo.",
        ),
        sheet=Sheet("buscar", "Busca estas formas en un paseo y colorea las que encuentres."),
    ),
    11: Script(
        pages=(
            "Fábula contaba cuentos y nunca contaba el mismo dos veces.",
            "Le pidieron el final de uno del martes y no se acordaba.",
            "Así que inventó otro mejor. Los finales, dijo, son de quien los cuenta.",
        ),
        sheet=Sheet(
            "dibujar",
            "Que dibuje aquí cómo termina su cuento. Escribid debajo lo que os cuente.",
            prompt="Y entonces...",
        ),
    ),
    12: Script(
        pages=(
            "Mar era enorme. Tan grande que creía que no necesitaba a nadie.",
            "Un día quedó encallada en la arena. Empujó y empujó, y no se movió.",
            "Vinieron veinte peces pequeños y empujaron a la vez. Mar volvió al agua.",
        ),
        sheet=Sheet("recortar", "Recortad las piezas entre los dos. Una cada uno, por turnos."),
    ),
}


def get_script(week_index: int) -> Script:
    return SCRIPTS[week_index]
