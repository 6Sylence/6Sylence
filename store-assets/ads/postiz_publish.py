#!/usr/bin/env python3
"""
Programa el lote de 10 publicaciones en Instagram a través de Postiz.

La clave NUNCA se escribe aquí: se lee de la variable de entorno POSTIZ_API_KEY.
Para Postiz autoalojado, exporta también POSTIZ_BASE_URL apuntando a tu backend
(por ejemplo https://postiz.midominio.com/api/public/v1).

Uso:
    export POSTIZ_API_KEY='...'
    python3 postiz_publish.py --list                 # ver canales conectados
    python3 postiz_publish.py --canal <id>           # simulacro (no publica nada)
    python3 postiz_publish.py --canal <id> --confirmar   # programa de verdad

Por defecto NO hace nada irreversible: sin --confirmar solo imprime el plan.
"""
import argparse, json, os, sys, datetime as dt, urllib.request, urllib.error, mimetypes, uuid

BASE = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com/public/v1").rstrip("/")
CLAVE = os.environ.get("POSTIZ_API_KEY", "")
AQUI = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(AQUI, "out")


def pedir(metodo, ruta, cuerpo=None, campos=None, archivo=None):
    url = f"{BASE}{ruta}"
    cab = {"Authorization": CLAVE}
    datos = None
    if archivo:
        lim = "----postiz" + uuid.uuid4().hex
        tipo = mimetypes.guess_type(archivo)[0] or "application/octet-stream"
        cuerpo_b = bytearray()
        for k, v in (campos or {}).items():
            cuerpo_b += (f"--{lim}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
        nombre = os.path.basename(archivo)
        cuerpo_b += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; "
                     f"filename=\"{nombre}\"\r\nContent-Type: {tipo}\r\n\r\n").encode()
        cuerpo_b += open(archivo, "rb").read() + f"\r\n--{lim}--\r\n".encode()
        datos = bytes(cuerpo_b)
        cab["Content-Type"] = f"multipart/form-data; boundary={lim}"
    elif cuerpo is not None:
        datos = json.dumps(cuerpo).encode()
        cab["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=datos, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            crudo = r.read().decode()
            return json.loads(crudo) if crudo.strip() else {}
    except urllib.error.HTTPError as e:
        detalle = e.read().decode()[:500]
        raise SystemExit(f"✗ {metodo} {ruta} → HTTP {e.code}\n  {detalle}")


def fechas(inicio, n):
    """Lunes, miércoles y viernes a las 19:30 de Madrid (CEST = UTC+2)."""
    salida, d = [], inicio
    while len(salida) < n:
        if d.weekday() in (0, 2, 4):
            salida.append(dt.datetime.combine(d, dt.time(17, 30)))   # 19:30 Madrid
        d += dt.timedelta(days=1)
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="lista los canales conectados")
    ap.add_argument("--canal", help="id de la integración de Instagram")
    ap.add_argument("--inicio", help="fecha del primer post, AAAA-MM-DD")
    ap.add_argument("--confirmar", action="store_true", help="programa de verdad")
    ap.add_argument("--hashtags-en-comentario", action="store_true",
                    help="manda los hashtags como primer comentario en vez de en el pie")
    a = ap.parse_args()

    if not CLAVE:
        raise SystemExit("✗ Falta POSTIZ_API_KEY en el entorno.")

    if a.list:
        for i in pedir("GET", "/integrations"):
            print(f"  {i.get('id')}  {i.get('providerIdentifier','?'):12s}  {i.get('name','')}"
                  f"  {'[deshabilitado]' if i.get('disabled') else ''}")
        return

    if not a.canal:
        raise SystemExit("✗ Indica --canal <id>. Sácalo con --list.")

    posts = json.load(open(os.path.join(AQUI, "postiz_posts.json")))
    inicio = (dt.date.fromisoformat(a.inicio) if a.inicio
              else dt.date.today() + dt.timedelta(days=1))
    cuando = fechas(inicio, len(posts))

    print(f"Canal: {a.canal}   ·   {len(posts)} publicaciones   ·   "
          f"{'PROGRAMANDO' if a.confirmar else 'SIMULACRO (no se envía nada)'}\n")

    for p, f in zip(posts, cuando):
        img = os.path.join(IMGS, p["imagen"])
        if not os.path.exists(img):
            raise SystemExit(f"✗ Falta la imagen {img}")
        print(f"  {f:%a %d/%m %H:%M} UTC  ·  {p['titulo']:22s}  ·  {p['imagen']}")
        if not a.confirmar:
            continue

        subida = pedir("POST", "/upload", archivo=img)
        valores = [{"content": p["pie"] + ("" if a.hashtags_en_comentario
                                           else "\n\n" + p["hashtags"]),
                    "image": [subida]}]
        if a.hashtags_en_comentario:
            valores.append({"content": p["hashtags"], "image": []})

        pedir("POST", "/posts", cuerpo={
            "type": "schedule",
            "date": f.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "shortLink": False,
            "tags": [],
            "posts": [{
                "integration": {"id": a.canal},
                "value": valores,
                "settings": {"__type": "instagram", "post_type": "post",
                             "collaborators": []},
            }],
        })
        print("      ✓ programada")

    if not a.confirmar:
        print("\nNada enviado. Repite con --confirmar para programarlas.")


if __name__ == "__main__":
    main()
