#!/usr/bin/env python3
# Genera el JSONL de variables para bulkOperationRunMutation:
# título SEO "Nombre | SRHOOD" (≤60) para productos sin él, y arregla
# descripciones truncadas a mitad de frase o ausentes.
import json, re

SRC = "bulk-products.jsonl"
OUT = "bulk-seo-vars.jsonl"

# palabras que delatan un corte a mitad de frase justo antes de ". Envío"
BROKEN_TAIL = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
               "al", "y", "o", "con", "para", "por", "que", "su", "sus", "más",
               "entre", "sobre", "como", "en", "se", "es", "the"}
ENVIO = "Envío a toda España · Devoluciones fáciles."

def gen_title(title):
    t = title.strip()
    if len(t) <= 51:
        return f"{t} | SRHOOD"
    # sin la parte de color "— Color" si así cabe
    base = t.split(" — ")[0].strip()
    if len(base) <= 51:
        return f"{base} | SRHOOD"
    return t[:60]

def is_broken(desc):
    m = re.search(r"([\wÁÉÍÓÚÑáéíóúñ]+)\.\s+Envío a toda España", desc)
    if not m:
        return False
    return m.group(1).lower() in BROKEN_TAIL

def gen_desc(title, old):
    if old and not is_broken(old):
        return None  # se conserva tal cual
    base = title.split(" — ")[0].strip()
    return f"{base} de SRHOOD: streetwear original de la Street Royalty. {ENVIO}"

n_total = n_out = n_title = n_desc = 0
with open(SRC) as f, open(OUT, "w") as out:
    for line in f:
        p = json.loads(line)
        n_total += 1
        seo = p.get("seo") or {}
        old_t, old_d = seo.get("title"), seo.get("description")
        new_t = old_t
        new_d = old_d
        changed = False
        if not old_t:
            new_t = gen_title(p["title"])
            n_title += 1
            changed = True
        fixed = gen_desc(p["title"], old_d)
        if fixed is not None:
            new_d = fixed
            n_desc += 1
            changed = True
        if not changed:
            continue
        if new_d is None:
            new_d = gen_desc(p["title"], None)
        out.write(json.dumps({"product": {"id": p["id"],
                                          "seo": {"title": new_t, "description": new_d}}},
                             ensure_ascii=False) + "\n")
        n_out += 1

print(f"total={n_total} a_actualizar={n_out} titulos_nuevos={n_title} descs_arregladas={n_desc}")
