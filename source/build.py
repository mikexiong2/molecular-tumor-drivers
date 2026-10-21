"""Build ../index.html for any static host. Python 3 standard library only."""
import json
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parent
data = dict(entities=[], sources={}, coverage=[])
for name in ['visceral', 'epithelial', 'neuro_mesent', 'heme', 'supplement']:
    part = json.loads((root / 'data' / f'{name}.json').read_text(encoding='utf-8'))
    for key, value in part['sources'].items():
        if key in data['sources'] and data['sources'][key] != value:
            raise ValueError(f'Conflicting source key: {key}')
        data['sources'][key] = value
    data['entities'].extend(part['entities'])
    data['coverage'].append(part['coverage'])

# Editorial corrections applied here so assembly remains reproducible.
by_id = {x['id']: x for x in data['entities']}
by_id['h_aml']['snv'].append('Cooperating / adverse biology — TP53 inactivation in a subset')
by_id['e_melanoma']['pitfall'] += ' Kinase fusions also occur in benign Spitz tumors and do not alone establish melanoma.'
by_id['s_gist']['aliases'].extend(['gastric stromal tumor', 'intestinal stromal tumor'])
by_id['v_pancreatoblastoma']['cnv'] = ['Characteristic — 11p deletion in a subset']
by_id['v_pancreatoblastoma']['other'].append('Alternative mechanism — 11p copy-neutral loss of heterozygosity')
by_id['v_parathyroid_carcinoma']['cnv'] = ['Driver — CDC73 deletion in a subset']
by_id['v_parathyroid_carcinoma']['other'].append('Alternative second hit — copy-neutral loss of heterozygosity affecting CDC73')
by_id['nm-rms']['cnv'] = ['Cooperating — MYCN/CDK4 amplification (subsets)']
by_id['nm-rms']['other'].append('Cooperating — 11p15 allelic imbalance / imprinting abnormalities; these need not alter copy number')

ids = [x['id'] for x in data['entities']]
assert len(ids) == len(set(ids)), 'Duplicate entity ID'
assert len({x['name'] for x in data['entities']}) == len(ids), 'Duplicate name'
for x in data['entities']:
    for key in ['id','name','system','anchor','pitfall']:
        assert isinstance(x[key],str) and x[key].strip(), (x['id'],key)
    for key in ['snv','cnv','rearr','other','aliases','refs']:
        assert isinstance(x[key],list) and all(isinstance(v,str) for v in x[key]), (x['id'],key)
    assert x['refs'], x['id']
    assert all(k in data['sources'] for k in x['refs']), x['id']
for key, src in data['sources'].items():
    assert src['url'].startswith('https://'), key

order = list(dict.fromkeys(x['system'] for x in data['entities']))
data['entities'].sort(key=lambda x:order.index(x['system']))
data['reviewed'] = '2026-10-19'
payload = json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
template = (root/'template.html').read_text(encoding='utf-8')
assert template.count('__DATA__') == 1
html = template.replace('__DATA__', payload)
(root.parent/'index.html').write_text(html, encoding='utf-8')
(root/'atlas.json').write_text(json.dumps(data,ensure_ascii=False,indent=2), encoding='utf-8')
print(json.dumps({'entries':len(ids),'groups':len(order),'sources':len(data['sources']),
                  'bytes':len(html.encode()),'by_group':dict(Counter(x['system'] for x in data['entities']))},indent=2))
