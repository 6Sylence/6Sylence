#!/usr/bin/env python3
"""
Publica lotes en Instagram y Facebook a través de Postiz.

La clave NUNCA se escribe aquí: se lee de POSTIZ_API_KEY. Para Postiz autoalojado,
exporta además POSTIZ_BASE_URL con tu backend.

    export POSTIZ_API_KEY='...'
    python3 postiz_publish.py --list
    python3 postiz_publish.py --lote lotes/lote-02.json --imagenes out/lote02 \
        --canal <ig>,<fb> --confirmar

Sin --confirmar no sale nada: solo imprime el plan.

## Por qué hay un fichero de estado

Un lote de cien en dos canales son doscientas llamadas y casi una hora de reloj.
Cualquier cosa —un 429, un corte, un Ctrl-C— deja el lote a medias, y sin registro
la única forma de saber por dónde iba es mirar el perfil a ojo. `lotes/estado-*.json`
anota cada publicación con su id de Postiz en cuanto sale, así que relanzar el mismo
comando continúa exactamente donde se quedó y **nunca repite una que ya salió**.

Cuando una pieza sale en algún canal, su handle se apunta en `lotes/publicados.json`,
que es lo que lee `seleccionar.py` para que el lote siguiente no la vuelva a elegir.

## El tope de 50

Instagram no acepta más de 50 publicaciones por cuenta y 24 horas vía API. No es una
política nuestra: la número 51 la rechaza Meta. El script lleva la cuenta en ventana
móvil sobre el propio fichero de estado y para al llegar al tope, diciendo cuántas
quedan y cuándo se puede seguir, en vez de estrellarse contra el límite.
"""
import argparse, json, os, time, datetime as dt
import urllib.request, urllib.error, mimetypes, uuid

BASE = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com/public/v1").rstrip("/")
CLAVE = os.environ.get("POSTIZ_API_KEY", "")
AQUI = os.path.dirname(os.path.abspath(__file__))
LOTES = os.path.join(AQUI, "lotes")
PUBLICADOS = os.path.join(LOTES, "publicados.json")

TOPE_24H = {"instagram": 50, "facebook": 50}


def pedir(metodo, ruta, cuerpo=None, archivo=None, reintentos=4):
    """Llamada con reintento exponencial ante 429/5xx: Postiz limita por hora."""
    url = f"{BASE}{ruta}"
    for intento in range(reintentos):
        cab = {"Authorization": CLAVE}
        datos = None
        if archivo:
            lim = "----postiz" + uuid.uuid4().hex
            tipo = mimetypes.guess_type(archivo)[0] or "application/octet-stream"
            b = bytearray()
            b += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; "
                  f"filename=\"{os.path.basename(archivo)}\"\r\n"
                  f"Content-Type: {tipo}\r\n\r\n").encode()
            b += open(archivo, "rb").read() + f"\r\n--{lim}--\r\n".encode()
            datos = bytes(b)
            cab["Content-Type"] = f"multipart/form-data; boundary={lim}"
        elif cuerpo is not None:
            datos = json.dumps(cuerpo).encode()
            cab["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=datos, headers=cab, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                crudo = r.read().decode()
                return json.loads(crudo) if crudo.strip() else {}
        except urllib.error.HTTPError as e:
            detalle = e.read().decode()[:400]
            if e.code in (429, 500, 502, 503, 504) and intento < reintentos - 1:
                espera = 30 * (2 ** intento)
                print(f"      · HTTP {e.code}, reintento en {espera}s")
                time.sleep(espera)
                continue
            raise RuntimeError(f"HTTP {e.code} en {metodo} {ruta}: {detalle}")
        except urllib.error.URLError as e:
            if intento < reintentos - 1:
                time.sleep(15)
                continue
            raise RuntimeError(f"{metodo} {ruta}: {e}")


# ── estado ────────────────────────────────────────────────────────────────────
def ruta_estado(lote):
    return os.path.join(LOTES, "estado-" + os.path.basename(lote))


def leer(path, defecto):
    return json.load(open(path)) if os.path.exists(path) else defecto


def escribir(path, datos):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(datos, open(path, "w"), ensure_ascii=False, indent=1)


def recientes(estado, canal, horas=24):
    """Cuántas han salido por ese canal en la ventana móvil."""
    corte = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=horas)
    n = 0
    for v in estado.values():
        if v["canal"] != canal:
            continue
        if dt.datetime.fromisoformat(v["ts"]) > corte:
            n += 1
    return n


def marcar_publicado(handle):
    ya = set(leer(PUBLICADOS, []))
    if handle not in ya:
        ya.add(handle)
        escribir(PUBLICADOS, sorted(ya))


# ── publicación ───────────────────────────────────────────────────────────────
def publicar(post, canal, imagen, hashtags_en_comentario):
    subida = pedir("POST", "/upload", archivo=imagen)
    pie = post["pie"] if hashtags_en_comentario else post["pie"] + "\n\n" + post["hashtags"]
    valores = [{"content": pie, "image": [subida]}]
    if hashtags_en_comentario:
        valores.append({"content": post["hashtags"], "image": []})
    tipo = canal["identifier"]
    r = pedir("POST", "/posts", cuerpo={
        "type": "now",
        "date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "shortLink": False,
        "tags": [],
        "posts": [{
            "integration": {"id": canal["id"]},
            "value": valores,
            "settings": ({"__type": "instagram", "post_type": "post", "collaborators": []}
                         if tipo == "instagram" else {"__type": "facebook"}),
        }],
    })
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--canal", help="ids de integración separados por coma")
    ap.add_argument("--lote", default="lotes/lote-02.json")
    ap.add_argument("--imagenes", default="out/lote02")
    ap.add_argument("--confirmar", action="store_true", help="publica de verdad")
    ap.add_argument("--pausa", type=int, default=12, help="segundos entre publicaciones")
    ap.add_argument("--hashtags-en-comentario", action="store_true")
    ap.add_argument("--desde", type=int, default=1)
    ap.add_argument("--hasta", type=int, default=10 ** 6)
    ap.add_argument("--tope", type=int, help="máximo por canal y 24 h (por defecto 50)")
    a = ap.parse_args()

    if not CLAVE:
        raise SystemExit("✗ Falta POSTIZ_API_KEY en el entorno.")

    integraciones = pedir("GET", "/integrations")
    if a.list:
        for i in integraciones:
            print(f"  {i.get('id')}  {i.get('identifier','?'):12s}  "
                  f"{i.get('name','')}  {'[deshabilitado]' if i.get('disabled') else ''}")
        return

    if not a.canal:
        raise SystemExit("✗ Indica --canal <id>[,<id>]. Sácalos con --list.")

    porid = {i["id"]: i for i in integraciones}
    canales = []
    for cid in a.canal.split(","):
        cid = cid.strip()
        if cid not in porid:
            raise SystemExit(f"✗ El canal {cid} no está en /integrations.")
        canales.append(porid[cid])

    ruta_lote = a.lote if os.path.isabs(a.lote) else os.path.join(AQUI, a.lote)
    dir_img = a.imagenes if os.path.isabs(a.imagenes) else os.path.join(AQUI, a.imagenes)
    posts = [p for p in json.load(open(ruta_lote)) if a.desde <= p["n"] <= a.hasta]

    est_path = ruta_estado(ruta_lote)
    estado = leer(est_path, {})

    print(f"Lote {os.path.basename(ruta_lote)} · {len(posts)} piezas · "
          f"canales: {', '.join(c['identifier'] for c in canales)}")
    print(f"Ya publicadas según el estado: {len(estado)} envíos")
    print(f"Modo: {'PUBLICACIÓN INMEDIATA' if a.confirmar else 'SIMULACRO'}\n")

    hechas, saltadas, topadas, fallos = 0, 0, {}, []
    for p in posts:
        imagen = os.path.join(dir_img, p["imagen"])
        if not os.path.exists(imagen):
            raise SystemExit(f"✗ Falta la imagen {imagen}")
        for c in canales:
            clave = f'{p["n"]}:{c["id"]}'
            if clave in estado:
                saltadas += 1
                continue
            tope = a.tope or TOPE_24H.get(c["identifier"], 50)
            if recientes(estado, c["id"]) >= tope:
                topadas[c["identifier"]] = topadas.get(c["identifier"], 0) + 1
                continue
            print(f'  [{p["n"]:03d}] {p["display"][:22]:22s} → {c["identifier"]}')
            if not a.confirmar:
                continue
            try:
                r = publicar(p, c, imagen, a.hashtags_en_comentario)
            except RuntimeError as e:
                print(f"       ✗ {e}")
                fallos.append((p["n"], c["identifier"], str(e)[:120]))
                continue
            estado[clave] = {"canal": c["id"], "red": c["identifier"],
                             "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                             "respuesta": str(r)[:200]}
            escribir(est_path, estado)          # se guarda en cada envío, no al final
            marcar_publicado(p["handle"])
            hechas += 1
            time.sleep(a.pausa)

    print(f"\n{hechas} publicadas · {saltadas} ya estaban · {len(fallos)} fallos")
    if topadas:
        for red, n in topadas.items():
            print(f"  · {red}: {n} en espera por el tope de 50/24 h. "
                  f"Relanza el mismo comando mañana y sigue solo,")
            print(f"    porque el estado ya sabe cuáles salieron.")
    if fallos:
        print("\nFallos:")
        for n, red, e in fallos:
            print(f"  [{n:03d}] {red}: {e}")
    if a.confirmar:
        print(f"\nEstado: {est_path}")
        print("Los textos alternativos van en el campo `alt` del lote; Postiz no los "
              "transmite y hay que pegarlos en la app.")
    else:
        print("\nNada enviado. Repite con --confirmar.")


if __name__ == "__main__":
    main()
