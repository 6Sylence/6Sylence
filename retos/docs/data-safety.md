# Formulario Data Safety de Google Play

Respuestas al formulario **Seguridad de los datos** de Play Console, con la línea de
código que justifica cada una. Google contrasta lo que declaras aquí con lo que hace la
app; una respuesta que no cuadre con el binario es motivo de retirada, y en apps para
menores lo revisan a mano.

**Regla al mantener esto:** si tocas un endpoint o metes un SDK, vuelve aquí antes de
subir la siguiente versión.

---

## Recopilación y uso

### Información personal

| Tipo | ¿Se recopila? | ¿Se comparte? | Obligatorio | Finalidad | Dónde está en el código |
|---|---|---|---|---|---|
| Dirección de correo | **Sí** | No | Sí | Gestión de la cuenta | `models.py` → `Parent.email` |
| Nombre | **Sí** | No | Sí | Funcionalidad de la app | `models.py` → `Child.name` |
| Otra información personal | No | — | — | — | — |

> El nombre que se recoge es el del menor y **puede ser un mote**: la app lo dice
> expresamente en la pantalla de alta del perfil (`app/onboarding/child.tsx`). Aun así se
> declara como nombre, porque el formulario pregunta por el dato, no por su exactitud.

### Información financiera

| Tipo | ¿Se recopila? | ¿Se comparte? | Finalidad | Dónde |
|---|---|---|---|---|
| Historial de compras | **Sí** | No | Gestión de la cuenta | `models.py` → `Entitlement.product_id`, `status`, `expires_at` |
| Datos de pago | **No** | — | — | Los procesa Google Play; la app nunca los ve |

### Actividad en la app

| Tipo | ¿Se recopila? | ¿Se comparte? | Finalidad | Dónde |
|---|---|---|---|---|
| Interacciones en la app | **Sí** | No | Funcionalidad de la app | `models.py` → `WeekProgress.completed_activity_ids` |
| Historial de búsqueda | No | — | — | No hay buscador |
| Apps instaladas | No | — | — | — |

### Lo que NO se recopila

Todas estas categorías se declaran **no recopiladas**, y conviene saber por qué se puede
afirmar con seguridad:

| Categoría | Por qué no |
|---|---|
| Ubicación | No se pide el permiso. `app.json` lo bloquea explícitamente |
| Fotos y vídeos | La validación por foto **no sube nada**: `ActivityCompleteRequest` solo tiene un booleano y no existe campo para imagen |
| Archivos y documentos | La app no accede al almacenamiento |
| Audio | Sin permiso de micrófono |
| Contactos | Sin permiso de contactos |
| Calendario | — |
| Mensajes | — |
| Salud y forma física | Las áreas de desarrollo son etiquetas de contenido, no medidas de nadie |
| ID de dispositivo o de otro tipo | No se usa identificador publicitario ni de dispositivo |
| Rendimiento de la app (fallos, diagnóstico) | No hay SDK de *crash reporting*. **Si añades Sentry o similar, hay que declararlo** |

## Prácticas de seguridad

| Pregunta | Respuesta | Justificación |
|---|---|---|
| ¿Los datos se cifran en tránsito? | **Sí** | Todo el tráfico va por HTTPS |
| ¿Se puede solicitar la eliminación de los datos? | **Sí** | `DELETE /api/auth/me`, accesible desde Zona de adultos → Borrar mi cuenta |
| ¿Sigue las Play Families Policy? | **Sí** | Ver `publicacion-play.md` |
| ¿Ha pasado una validación de seguridad independiente? | **No** | No la hemos hecho. No marques que sí |

## Enlace de eliminación de cuenta

Google pide **dos vías**, no una:

1. **Dentro de la app** — hecho: Zona de adultos → Borrar mi cuenta.
2. **Una URL pública** donde alguien que ya desinstaló la app pueda pedir el borrado.
   **Esto falta.** Hay que publicar una página en `[dominio]/borrar-cuenta` y declararla
   en el formulario. Sin ella, el formulario queda incompleto.

## Público objetivo y contenido

| Pregunta | Respuesta |
|---|---|
| Grupos de edad objetivo | **Menores de 5 años** y **6-8 años** |
| ¿La app atrae también a adultos? | Sí — el comprador y quien valida es el adulto |
| ¿Muestra anuncios? | **No** |
| ¿Tiene compras integradas? | **Sí**, suscripción |

Declarar menores como público objetivo mete la app en la **Families Policy**, con todo lo
que eso implica (ver `publicacion-play.md`). No hay forma de evitarlo diciendo que es
para adultos: el contenido es claramente infantil y Google lo revisa.

## Clasificación de contenido (IARC)

Respuestas esperadas del cuestionario, que deberían dar **PEGI 3 / ESRB Everyone**:

- Violencia, sexo, lenguaje soez, drogas, juego de azar: **no** a todo.
- ¿Los usuarios pueden interactuar o comunicarse entre sí? **No.** No hay chat, ni
  comentarios, ni nada social. Responder «sí» aquí sube la clasificación y dispara
  requisitos que no queremos.
- ¿Comparte la ubicación con otros usuarios? **No.**
- ¿Permite comprar artículos digitales? **Sí.**
