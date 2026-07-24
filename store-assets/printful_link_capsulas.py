#!/usr/bin/env python3
"""Pasada de reparación: revincula variantes que quedaron sin variant_id (429s)."""
import json
import os
import time
import urllib.request

SP = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ["PRINTFUL_API_KEY"]
STORE = "18383330"

import importlib.util
spec = importlib.util.spec_from_file_location("link_printful", SP + "/link_printful.py")
# solo importamos MANIFEST y api sin ejecutar el main: link_printful ejecuta al importar,
# así que duplicamos lo necesario aquí.

CDN = "https://cdn.shopify.com/s/files/1/1003/6874/4832/files"
SHOE_QT = ["shoe_quarters_left", "shoe_quarters_right", "shoe_tongue_left", "shoe_tongue_right"]
MANIFEST = [
    ("Camiseta Nube Imperial", [("default", "nube_tee_print.png")],
     [4111, 4112, 4113, 4114, 4115], "27.95"),
    ("Hoodie Nube Imperial", [("default", "nube_hoodie_print.png")],
     [11491, 11492, 11493, 11494, 11495], "49.95"),
    ("Zapatillas Altas Nube Imperial Hombre", [(p, "nube_hitop_tile.png") for p in SHOE_QT],
     [12903, 12904, 12905, 12906, 12907, 12908, 12909, 12910, 12911, 12912, 12913, 12914,
      12915, 12916, 12918, 12919, 12920], "74.95"),
    ("Zapatillas Slip-On Nube Imperial Mujer",
     [("shoe_left", "nube_slipon_tile.png"), ("shoe_right", "nube_slipon_tile.png")],
     [14721, 14722, 14723, 14724, 14725, 14726, 14727, 14728, 14729, 14730, 14731, 14732,
      14733, 14734, 14735], "59.95"),
    ("Calcetines Nube Imperial", [("default", "nube_socks_print.png")],
     [7290, 7291, 7292], "14.95"),
    ("Bucket Hat Nube Imperial", [
        ("outside_front", "nube_bucket_out.png"), ("outside_back", "nube_bucket_out.png"),
        ("inside_front", "nube_bucket_in.png"), ("inside_back", "nube_bucket_in.png")],
     [16360, 16361], "34.95"),
    ("Camiseta Salpicadura Atelier", [("default", "salp_tee_print.png")],
     [4011, 4012, 4013, 4014, 4015], "27.95"),
    ("Sudadera Salpicadura Atelier", [("default", "salp_sweat_print.png")],
     [5426, 5427, 5428, 5429, 5430], "42.95"),
    ("Camiseta Manga Larga Salpicadura", [("default", "salp_ls_print.png")],
     [10142, 10143, 10144, 10145, 10146], "32.95"),
    ("Zapatillas Lona Salpicadura Hombre", [(p, "salp_lona_tile.png") for p in SHOE_QT],
     [14844, 14845, 14846, 14847, 14848, 14849, 14850, 14851, 14852, 14853, 14854, 14855,
      14856, 14857, 14858, 14859, 14860], "59.95"),
    ("Zapatillas Deportivas Salpicadura Mujer",
     [("shoe_left", "salp_deportivas_print.png"), ("shoe_right", "salp_deportivas_print.png")],
     [16385, 16386, 16387, 16388, 16389, 16390, 16391, 16392, 16393, 16394, 16395, 16396,
      16397, 16398, 16399], "74.95"),
    ("Chanclas Salpicadura", [("default", "salp_chanclas_print.png")],
     [10170, 10171, 10172], "24.95"),
]


def api(m, p, b=None):
    for attempt in range(10):
        req = urllib.request.Request(
            "https://api.printful.com" + p,
            data=json.dumps(b).encode() if b else None,
            headers={"Authorization": "Bearer " + KEY, "X-PF-Store-Id": STORE,
                     "Content-Type": "application/json"}, method=m)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode())
            except Exception:
                body = {"code": e.code}
            if e.code == 429:
                time.sleep(65)
                continue
            return body
    return {"code": 429, "error": "gave up"}


def find_sync_product(name):
    from urllib.parse import quote
    r = api("GET", f"/sync/products?search={quote(name)}&limit=20")
    for p in r.get("result", []):
        if p["name"].startswith(name):
            return p
    return None


final = {}
for name, files, vids, price in MANIFEST:
    sp = None
    for _ in range(30):
        sp = find_sync_product(name)
        if sp:
            break
        time.sleep(15)
    if not sp:
        final[name] = {"error": "no importado"}
        print(name, "NO IMPORTADO", flush=True)
        continue
    det = api("GET", f"/sync/products/{sp['id']}")
    svs = det["result"]["sync_variants"]
    if len(svs) != len(vids):
        final[name] = {"error": f"variantes {len(svs)} != {len(vids)}"}
        print(name, "MISMATCH", flush=True)
        continue
    fl = [{"type": t, "url": f"{CDN}/{f}"} for t, f in files]
    fixed = 0
    for sv, vid in zip(svs, vids):
        if sv.get("variant_id") == vid and sv.get("synced"):
            continue
        body = {"variant_id": vid, "retail_price": price, "is_ignored": False, "files": fl}
        r = api("PUT", f"/sync/variant/{sv['id']}", body)
        if r.get("code") == 200:
            fixed += 1
        else:
            print(name, sv["id"], "ERR", str(r)[:160], flush=True)
        time.sleep(2.5)
    det2 = api("GET", f"/sync/products/{sp['id']}")
    spd = det2["result"]["sync_product"]
    final[name] = {"sync_id": sp["id"], "synced": spd.get("synced"),
                   "variants": spd.get("variants"), "is_ignored": spd.get("is_ignored"),
                   "fixed_now": fixed}
    print(name, "->", final[name], flush=True)

json.dump(final, open(SP + "/final_link_report.json", "w"), indent=1, ensure_ascii=False)
print("REPAIR DONE", flush=True)
