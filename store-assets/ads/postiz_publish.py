#!/usr/bin/env python3
"""
Publica lotes de posts en Instagram a través de Postiz.

La clave NUNCA se escribe aquí: se lee de POSTIZ_API_KEY. Para Postiz
autoalojado, exporta además POSTIZ_BASE_URL con tu backend
(p. ej. https://postiz.midominio.com/api/public/v1).

    export POSTIZ_API_KEY='...'
    python3 postiz_publish.py --list                          # canales conectados
    python3 postiz_publish.py --canal <id>                    # simulacro
    python3 postiz_publish.py --canal <id> --confirmar        # publica YA
    python3 postiz_publish.py --canal <id> --lote lote2.json --confirmar

Sin --confirmar no sale nada: solo imprime el plan.
"""
import argparse, json, os, time, datetime as dt
import urllib.request, urllib.error, mimetypes, uuid

BASE = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com/public/v1").rstrip("/")
CLAVE = os.environ.get("POSTIZ_API_KEY", "")
AQUI = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(AQUI, "out", "jpg")


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
            raise SystemExit(f"✗ {metodo} {ruta} → HTTP {e.code}\n  {detalle}")
        except urllib.error.URLError as e:
            if intento < reintentos - 1:
                time.sleep(15)
                continue
            raise SystemExit(f"✗ {metodo} {ruta} → {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--canal", help="id de la integración de Instagram")
    ap.add_argument("--lote", default="postiz_posts.json", help="fichero del lote")
    ap.add_argument("--confirmar", action="store_true", help="publica de verdad")
    ap.add_argument("--pausa", type=int, default=20,
                    help="segundos entre publicaciones (evita el límite por hora)")
    ap.add_argument("--hashtags-en-comentario", action="store_true",
                    help="hashtags como primer comentario en vez de en el pie")
    ap.add_argument("--desde", type=int, default=1, help="reanudar desde el post nº N del lote")
    a = ap.parse_args()

    if not CLAVE:
        raise SystemExit("✗ Falta POSTIZ_API_KEY en el entorno.")

    if a.list:
        for i in pedir("GET", "/integrations"):
            # el campo de la plataforma se llama `identifier`, no `providerIdentifier`
            print(f"  {i.get('id')}  {i.get('identifier','?'):12s}  "
                  f"{i.get('name','')}  {'[deshabilitado]' if i.get('disabled') else ''}")
        return

    if not a.canal:
        raise SystemExit("✗ Indica --canal <id>. Sácalo con --list.")

    ruta_lote = a.lote if os.path.isabs(a.lote) else os.path.join(AQUI, a.lote)
    posts = json.load(open(ruta_lote))[a.desde - 1:]

    print(f"Lote: {os.path.basename(ruta_lote)}  ·  {len(posts)} publicaciones  ·  "
          f"canal {a.canal}\n"
          f"Modo: {'PUBLICACIÓN INMEDIATA' if a.confirmar else 'SIMULACRO (no se envía nada)'}\n")

    hechas, fallidas = [], []
    for k, p in enumerate(posts, start=a.desde):
        img = os.path.join(IMGS, p["imagen"])
        if not os.path.exists(img):
            raise SystemExit(f"✗ Falta la imagen {img}")
        print(f"  [{k:02d}] {p['titulo']:22s} · {p['imagen']}")
        if not a.confirmar:
            continue

        subida = pedir("POST", "/upload", archivo=img)
        pie = p["pie"] if a.hashtags_en_comentario else p["pie"] + "\n\n" + p["hashtags"]
        valores = [{"content": pie, "image": [subida]}]
        if a.hashtags_en_comentario:
            valores.append({"content": p["hashtags"], "image": []})

        r = pedir("POST", "/posts", cuerpo={
            "type": "now",
            "date": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "shortLink": False,
            "tags": [],
            "posts": [{
                "integration": {"id": a.canal},
                "value": valores,
                "settings": {"__type": "instagram", "post_type": "post",
                             "collaborators": []},
            }],
        })
        hechas.append((k, p["titulo"], p["alt"]))
        print("       ✓ publicada")
        print(f"       texto alternativo (pégalo en la app):\n       {p['alt']}")
        if k - a.desde + 1 < len(posts):
            time.sleep(a.pausa)

    if a.confirmar:
        print(f"\n{len(hechas)} publicadas.")
        print("\nTextos alternativos — Postiz no los transmite; ponlos en Instagram:")
        print("  post ··· → Editar → Editar texto alternativo")
        for k, t, alt in hechas:
            print(f"\n  [{k:02d}] {t}\n       {alt}")
        if fallidas:
            print("Fallidas:", fallidas)
    else:
        print("\nNada enviado. Repite con --confirmar para publicar.")


if __name__ == "__main__":
    main()
