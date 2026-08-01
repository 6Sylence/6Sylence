# Política de privacidad — Retos

**Borrador de trabajo. No lo publiques sin que lo revise un abogado.** Está escrito
leyendo el código, no una plantilla: describe exactamente lo que la app hace hoy. Si el
código cambia, este documento se queda desactualizado y deja de protegerte.

Los campos entre `[corchetes]` hay que rellenarlos antes de publicar.

Última actualización: `[fecha]`

---

## Quién es el responsable

`[Nombre o razón social]`, `[dirección]`, `[NIF]`. Contacto: `[correo]`.

## En una frase

Retos es una app que un adulto contrata para su hijo. La cuenta es del adulto. Del menor
guardamos dos datos —un nombre y una franja de edad— y nada más.

## Qué datos recogemos

### De la persona adulta que crea la cuenta

| Dato | Para qué | Obligatorio |
|---|---|---|
| Correo electrónico | Identificar la cuenta y poder iniciar sesión | Sí |
| Contraseña | Acceder a la cuenta. Se guarda cifrada con bcrypt, nunca en claro | Sí |
| Estado de la suscripción | Saber si el acceso está vigente | Sí |
| Fecha de alta | Gestionar la cuenta | Sí |

### Del niño o la niña

| Dato | Para qué | Obligatorio |
|---|---|---|
| Un nombre | Que la app se dirija a él o ella. Vale un mote; no hace falta el nombre real | Sí |
| Franja de edad (3-4 o 5-6) | Ajustar la dificultad de los retos | Sí |
| Un animal elegido | Personalizar la pantalla | No |

**No pedimos ni guardamos** la fecha de nacimiento, el sexo, el colegio, fotografías, la
voz, la ubicación, la agenda de contactos ni ningún identificador publicitario.

### Del uso de la app

| Dato | Para qué |
|---|---|
| Qué actividades ha validado el adulto y cuándo | Saber por qué semana va y si está completa |
| Qué recompensa eligió el niño cada semana | Mostrarle su premio |
| Códigos de recompensa física y si se han canjeado | Poder enviar el premio |

## Las fotos no salen del teléfono

Para validar un reto, la app propone al adulto hacer una foto de su hijo haciéndolo.
**Esa foto no se envía a ningún sitio.** Se queda en el teléfono y la app no la guarda ni
la sube: lo único que llega a nuestros servidores es la confirmación de que un adulto ha
dado el reto por hecho.

## Qué NO hacemos

- **No hay publicidad.** Ni propia ni de terceros.
- **No hay analítica de comportamiento.** No usamos SDK de seguimiento ni perfilamos a
  nadie, y menos a un menor.
- **No vendemos ni cedemos datos** a terceros con fines comerciales.
- **No tomamos decisiones automatizadas** que afecten a la persona usuaria.

## Con quién compartimos datos

Solo con quien hace falta para que la app funcione:

| Quién | Qué recibe | Por qué |
|---|---|---|
| `[proveedor de alojamiento]` | Los datos de la cuenta, alojados en sus servidores | Es donde vive la base de datos |
| Google Play | Los datos de la compra | Procesa el pago de la suscripción |

**Nunca vemos tu tarjeta.** El pago lo gestiona Google Play de principio a fin; nosotros
solo recibimos si la suscripción está activa o no.

## Dónde se guardan

En servidores situados en `[país o región]`. `[Si hay transferencias fuera del EEE,
indicar la garantía: cláusulas contractuales tipo, decisión de adecuación, etc.]`

## Cuánto tiempo

Mientras la cuenta exista. Al borrarla, todo se elimina de inmediato y de forma
irreversible: la cuenta, los perfiles de los hijos, su progreso y los códigos sin canjear.
No conservamos copia ni dejamos nada marcado como «borrado».

## Base legal

- **Ejecución de un contrato** (art. 6.1.b RGPD): para prestar el servicio que el adulto
  ha contratado. Es la base de todo lo anterior.
- **Obligación legal** (art. 6.1.c RGPD): para conservar las facturas el tiempo que exija
  la normativa fiscal.

No tratamos datos por interés legítimo ni pedimos consentimientos separados, porque no
hacemos nada que los necesite: sin publicidad ni analítica, no hay nada que consentir.

## Menores

El servicio lo contrata siempre una persona adulta. **El menor no tiene cuenta, ni
credenciales, ni forma de registrarse.** No nos dirigimos comercialmente a menores ni les
mostramos publicidad.

## Tus derechos

Puedes acceder, rectificar, suprimir, limitar y portar tus datos, y oponerte al
tratamiento.

- **Borrar la cuenta entera:** desde la app, en Zona de adultos → Borrar mi cuenta. Es
  inmediato.
- **Borrar solo el perfil de un hijo:** desde la app, en Zona de adultos → Perfiles.
- **Cualquier otra cosa:** escribe a `[correo]`. Respondemos en un mes como máximo.
- También puedes reclamar ante la Agencia Española de Protección de Datos
  (www.aepd.es).

**Borrar la cuenta no cancela la suscripción.** La suscripción se contrata con Google Play
y solo puedes cancelarla tú, desde Play → Pagos y suscripciones. Hazlo antes de borrar la
cuenta o seguirá cobrándose.

## Seguridad

Todo el tráfico viaja cifrado (HTTPS). Las contraseñas se guardan con bcrypt, así que ni
nosotros podemos leerlas. La sesión se almacena en el teléfono en el almacén seguro del
sistema (Android Keystore).

## Cambios

Si cambiamos esta política, actualizaremos la fecha de arriba y avisaremos dentro de la
app antes de que los cambios te afecten.
