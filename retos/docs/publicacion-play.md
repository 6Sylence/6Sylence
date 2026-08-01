# Publicar Retos en Google Play

Checklist accionable. El orden importa: hay pasos con espera obligatoria de semanas, así
que conviene empezarlos antes de tener la app terminada.

Las políticas de Play cambian a menudo. Todo lo que dice este documento hay que
**confirmarlo en la consola** en el momento de enviar; lo que se marca con ⚠️ es lo que
más se mueve.

---

## Lo que hay que saber antes de empezar

### El test cerrado no es opcional ⚠️

Una cuenta de desarrollador **personal** creada recientemente no puede publicar en
producción sin antes:

1. Ejecutar un **test cerrado con 12 testers** que hayan aceptado la invitación.
2. Mantenerlo **14 días seguidos**. Si un tester se sale, el contador puede reiniciarse.
3. Solicitar después el acceso a producción, que se revisa a mano.

Esto convierte la validación en obligatoria, no en opcional: son 12 familias reales
usando la app dos semanas. Trátalo como la fase de validación del producto, no como un
trámite — es exactamente la cohorte que dice si el bucle engancha.

**Una cuenta de organización con D-U-N-S no tiene ese requisito**, pero el alta es más
lenta y pide documentación de la empresa. Si vas en serio, merece la pena mirarlo antes
de darte de alta como particular.

### Declarar menores como público objetivo es irreversible en la práctica

En cuanto marcas «menores de 5 años» entras en la **Families Policy**. No hay atajo: el
contenido es infantil y Google lo revisa a mano.

---

## 1. Cuenta y facturación

- [ ] Alta en Play Console: **25 $, pago único**.
- [ ] Decidir **particular u organización** (ver arriba). Cambiar después es engorroso.
- [ ] Verificación de identidad: DNI y, en organización, documentación de la empresa.
- [ ] Configurar el **perfil de pagos** para cobrar las suscripciones.
- [ ] ⚠️ **Estado de comerciante (DSA).** Vendiendo en la UE hay que declararse comerciante
      y publicar nombre, dirección y contacto **en la ficha, visible para cualquiera**.
      Si trabajas desde casa, plantéate un domicilio fiscal o un buzón antes de llegar
      aquí.

## 2. La app

- [x] Borrado de cuenta dentro de la app — `DELETE /api/auth/me`, en Zona de adultos.
- [x] Barrera de adultos antes de la zona de padres, resuelta con una suma escrita en
      letra. Vive en la pantalla de destino, no en quien navega hasta ella, para que un
      enlace directo no la esquive.
- [x] Sin permisos innecesarios: `app.json` deja `permissions: []` y bloquea ubicación,
      cámara, micrófono y contactos.
- [x] Sin SDK de publicidad ni de analítica.
- [ ] **Firma de la app.** Alta en Play App Signing y guardar la clave de subida. Si la
      pierdes y no estás en App Signing, pierdes la app.
- [ ] ⚠️ **Nivel de API objetivo.** Play exige compilar contra un nivel reciente y lo sube
      cada año. Expo 54 ya apunta a uno actual, pero confírmalo en la consola: es motivo
      de rechazo automático.
- [ ] `versionCode` incremental en cada subida. Empieza en 1 (ya está puesto).
- [ ] Sustituir la tipografía DejaVu por una redondeada con licencia comercial.
- [ ] Iconos y gráfico de cabecera. Play pide icono 512×512 y *feature graphic*
      1024×500.

## 3. Contenido de la ficha

- [ ] Título, descripción breve y descripción completa. **Sin promesas de resultados**:
      «estimula la motricidad fina» sí; «mejora el CI» o «ayuda con el TDAH» no. Eso es
      publicidad engañosa y en infantil se persigue.
- [ ] Capturas de pantalla de teléfono. Que salga la zona del niño, no formularios.
- [ ] **Política de privacidad publicada en una URL accesible sin iniciar sesión.**
      Borrador en [`politica-privacidad.md`](politica-privacidad.md) — pásalo por un
      abogado.
- [ ] **Página web de solicitud de borrado de cuenta**, para quien ya desinstaló. Google
      pide esta vía además de la que hay dentro de la app. **Está pendiente.**
- [ ] Correo de contacto de soporte.

## 4. Declaraciones de la consola

- [ ] **Público objetivo:** menores de 5 años y 6-8 años.
- [ ] **Seguridad de los datos:** el formulario está respondido campo a campo en
      [`data-safety.md`](data-safety.md), con la línea de código que justifica cada
      respuesta.
- [ ] **Clasificación de contenido (IARC):** respuestas esperadas también en
      `data-safety.md`. Debería salir PEGI 3.
- [ ] **Anuncios:** declarar que la app **no contiene anuncios**.
- [ ] **Families Policy:** confirmar el cumplimiento. Lo que revisan:
  - Sin publicidad de terceros no certificada. *(No hay publicidad.)*
  - Sin recogida de identificadores publicitarios ni ubicación de menores. *(No se
    recogen.)*
  - Barrera de adultos antes de compras y enlaces externos. *(Implementada.)*
  - Contenido apropiado a la edad declarada.
- [ ] **App de noticias, COVID, finanzas:** no. Se pregunta igual.

## 5. Suscripción

- [ ] Crear el producto de suscripción en Play Console. **Tiene que ir por Google Play
      Billing**: la comisión es del 15% del primer millón de dólares al año y no se puede
      cobrar con Stripe dentro de la app.
- [ ] Configurar la prueba gratuita de 7 días (el backend ya la modela al registrarse).
- [ ] **Validar los recibos.** Hoy el webhook de facturación está cerrado por un secreto
      compartido pero **no valida contra Google Play**. Hay un `TODO` explícito en
      `routers/billing.py`. Con el secreto filtrado, se regalan suscripciones. Esto hay
      que cerrarlo antes de cobrar a nadie.
- [ ] **La recompensa física no puede pasar por Play Billing.** Los bienes físicos están
      excluidos: el canje ocurre en la web con el código, y así está construido.

## 6. Lanzamiento

1. [ ] **Test interno** (hasta 100 testers, sin espera). Para comprobar que el AAB
       instala y arranca.
2. [ ] **Test cerrado**: 12 testers, 14 días seguidos. ⚠️ Requisito para cuentas
       personales.
3. [ ] Solicitar **acceso a producción**. Revisión manual; cuenta con varios días.
4. [ ] Publicar, empezando por un despliegue por fases.

## Calendario realista

| Fase | Tiempo |
|---|---|
| Alta y verificación de la cuenta | 2-7 días (más si es organización) |
| Preparar ficha, política y assets | 3-5 días |
| Test interno | 1 día |
| **Test cerrado** | **14 días mínimo** |
| Revisión de acceso a producción | 3-7 días |
| Revisión de la publicación | 1-7 días, más en Familias |

**Del envío a estar en Play: entre tres y cinco semanas**, y eso con todo listo. El test
cerrado es el suelo: no se puede acelerar.

## Errores que tumban una app infantil

Por orden de frecuencia:

1. **Data Safety que no cuadra con el binario.** Declarar que no recoges algo que un SDK
   sí recoge. Por eso `data-safety.md` cita el código.
2. **Política de privacidad inaccesible**, caída, o que no menciona a los menores.
3. **Sin vía de borrado de cuenta.** Ya resuelto dentro de la app; falta la web.
4. **Público objetivo mal declarado**, intentando esquivar la Families Policy.
5. **Promesas educativas o de salud** en la descripción.
6. **Personajes con licencia.** Nada «inspirado en» Bluey, Peppa o Disney. Todo lo que
   genera `studio/` es original; que siga así.
