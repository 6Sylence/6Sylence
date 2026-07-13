#!/usr/bin/env python3
"""Limpia la promesa '15% de descuento automático' de descriptionHtml.
Uso: python3 clean_desc.py input.json output.json
input.json: [{"id":..., "handle":..., "descriptionHtml":...}]
output.json: [{"id","handle","cleanedHtml","changed","safe","reason"}]
Solo marca safe=true si la limpieza es verificable y acotada.
"""
import json, re, sys

CLAUSE = re.compile(
    r'\s*(?:[y+,]|e)?\s*(?:⭐|🎁|✨)?\s*15\s*%\s*de\s*(?:descuento|dto\.?)\s*autom[aá]tico'
    r'(?:\s*aplicado)?'
    r'(?:\s*en\s+(?:tu\s+)?(?:primera\s+compra|compra|el\s+carrito|carrito|el\s+pedido|pedido))?',
    re.IGNORECASE)

# <li>/<p>/<h3>/<span>/<div> cuyo contenido es SOLO la promo (sin tags anidados)
ELEMENT = re.compile(
    r'<(li|p|h3|h4|span|div|em|strong)\b[^>]*>\s*(?:⭐|🎁|✨|[-–·•])?\s*15\s*%\s*de\s*(?:descuento|dto\.?)\s*autom[aá]tico[^<]{0,90}</\1>',
    re.IGNORECASE)

EMPTY = re.compile(r'<(li|p|span|em|strong)\b[^>]*>\s*(?:&nbsp;)?\s*</\1>', re.IGNORECASE)
LEFTOVER = re.compile(r'15\s*%.{0,60}autom[aá]tico|autom[aá]tico.{0,60}15\s*%', re.IGNORECASE | re.DOTALL)

def clean(html):
    out = ELEMENT.sub('', html)
    out = CLAUSE.sub('', out)
    out = EMPTY.sub('', out)
    # arreglos cosméticos
    out = re.sub(r'\s+([.,])', r'\1', out)
    out = re.sub(r'[ \t]{2,}', ' ', out)
    return out

def main():
    items = json.load(open(sys.argv[1]))
    results = []
    for it in items:
        html = it['descriptionHtml']
        cleaned = clean(html)
        changed = cleaned != html
        reduction = len(html) - len(cleaned)
        safe = True
        reason = 'ok'
        if not changed:
            safe = False; reason = 'sin cambios (promo no encontrada en HTML)'
        elif LEFTOVER.search(cleaned):
            safe = False; reason = 'quedan restos de la promo tras limpiar'
        elif reduction > 600 or reduction < 0:
            safe = False; reason = f'reduccion sospechosa: {reduction} chars'
        results.append({'id': it['id'], 'handle': it.get('handle'),
                        'cleanedHtml': cleaned, 'changed': changed,
                        'safe': safe, 'reason': reason, 'reduction': reduction})
    json.dump(results, open(sys.argv[2], 'w'), ensure_ascii=False)
    ok = sum(1 for r in results if r['safe'])
    print(f"{ok}/{len(results)} seguros para actualizar")
    for r in results:
        if not r['safe']:
            print('SKIP', r['handle'], '-', r['reason'])

if __name__ == '__main__':
    main()
