"""Build ../index.html and ../tumor-driver-atlas.apkg for any static host. Python 3 standard library only."""
import hashlib
import html as html_lib
import json
import re
import sqlite3
import tempfile
import time
import zipfile
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
data = dict(entities=[], sources={}, coverage=[])
for name in ['visceral', 'epithelial', 'neuro_mesent', 'heme', 'supplement', 'updates_2026']:
    part = json.loads((root / 'data' / f'{name}.json').read_text(encoding='utf-8'))
    for key, value in part['sources'].items():
        if key in data['sources'] and data['sources'][key] != value:
            raise ValueError(f'Conflicting source key: {key}')
        data['sources'][key] = value
    data['entities'].extend(part['entities'])
    data['coverage'].append(part['coverage'])

# Editorial corrections and 2026 driver updates applied here so assembly remains reproducible.
by_id = {x['id']: x for x in data['entities']}

# Original editorial corrections
by_id['h_aml']['snv'].append('Cooperating / adverse biology — TP53 inactivation in a subset')
by_id['e_melanoma']['pitfall'] += ' Kinase fusions also occur in benign Spitz tumors and do not alone establish melanoma.'
by_id['s_gist']['aliases'].extend(['gastric stromal tumor', 'intestinal stromal tumor'])
by_id['v_pancreatoblastoma']['cnv'] = ['Characteristic — 11p deletion in a subset']
by_id['v_pancreatoblastoma']['other'].append('Alternative mechanism — 11p copy-neutral loss of heterozygosity')
by_id['v_parathyroid_carcinoma']['cnv'] = ['Driver — CDC73 deletion in a subset']
by_id['v_parathyroid_carcinoma']['other'].append('Alternative second hit — copy-neutral loss of heterozygosity affecting CDC73')
by_id['nm-rms']['cnv'] = ['Cooperating — MYCN/CDK4 amplification (subsets)']
by_id['nm-rms']['other'].append('Cooperating — 11p15 allelic imbalance / imprinting abnormalities; these need not alter copy number')

# November 2026 literature & WHO 5th/6th edition updates to existing entities
by_id['e_digital']['anchor'] = 'Digital papillary adenocarcinoma → HPV42-driven malignant sweat gland tumor.'
by_id['e_digital']['other'].append('Viral driver — human papillomavirus 42 (HPV42), classified as a low-risk HPV type yet recurrently driving digital papillary adenocarcinoma')
by_id['e_digital']['pitfall'] = 'HPV42 in situ hybridization or sequencing strongly supports the diagnosis and distinguishes it from benign acral adnexal mimics, though not every laboratory tests for HPV42 routinely.'
by_id['e_digital']['refs'].append('u_hpv42_dpa')

by_id['v_thymoma']['rearr'].extend([
    'Defining (metaplastic thymoma) — YAP1::MAML2',
    'Recurrent (aggressive type B2/B3 subset) — KMT2A::MAML2',
])
by_id['v_thymoma']['refs'].append('u_thymoma_fus')

by_id['h_aml']['snv'].append('Emerging high-risk subset — UBTF tandem duplications (UBTF-TD; menin-dependent)')
by_id['h_aml']['rearr'].append('Emerging high-risk subset — BCL11B structural variants / 14q32 enhancer hijacking')
by_id['h_aml']['pitfall'] += ' In WHO-HAEM5, NUP98 rearrangements (alongside PML::RARA, RUNX1::RUNX1T1, CBFB::MYH11, KMT2A, MECOM and NPM1) define AML regardless of the 20% blast threshold.'
by_id['h_aml']['refs'].extend(['u_aml_ubtf', 'u_aml_nup98'])

by_id['h_ball']['cnv'].append('Subset-defining (CDX2/UBTF) — 13q12 deletion retargeting the PAN3 enhancer to deregulate CDX2')
by_id['h_ball']['rearr'].append('Emerging high-risk subset — UBTF::ATXN7L3 (CDX2/UBTF subtype)')
by_id['h_ball']['refs'].extend(['u_all_2025', 'u_all_adult25'])

by_id['h_tall']['rearr'].append('High-risk subsets — SPI1 rearrangements; ETP-like KMT2A/MLLT10 and BCL11B-rearranged ETP-ALL')
by_id['h_tall']['refs'].extend(['u_all_2025', 'u_all_adult25'])

by_id['nm-mening']['cnv'].append('Grading (cIMPACT-NOW Update 8) — combined 1p and 22q loss upgrades morphologically grade 1 meningioma to CNS WHO grade 2')
by_id['nm-mening']['pitfall'] += ' cIMPACT-NOW Update 8 reaffirms TERT promoter mutation and CDKN2A/B homozygous deletion as sufficient for CNS WHO grade 3.'
by_id['nm-mening']['refs'].extend(['u_cimpact8', 'u_cimpact8_pmc'])

by_id['nm-rms']['rearr'].append('Intraosseous / spindle-epithelioid subsets — EWSR1/FUS::TFCP2 or MEIS1::NCOA2 fusions')
by_id['nm-rms']['pitfall'] += ' WHO Soft Tissue & Bone 6th ed. (Oct 2026) splits spindle cell/sclerosing RMS into molecularly distinct categories (VGLL2/NCOA2, MYOD1 L122R, and TFCP2/MEIS1-rearranged).'
by_id['nm-rms']['refs'].extend(['u_who6_stb', 'u_rms_tfcp2'])

by_id['nm-nonets']['pitfall'] += ' WHO Soft Tissue & Bone 6th ed. (Oct 2026) separates NFATC2-rearranged sarcoma and PATZ1-rearranged sarcoma into standalone entries (listed separately in this atlas).'
by_id['nm-nonets']['refs'].append('u_who6_stb')

by_id['nm-ehe']['pitfall'] += ' WHO Soft Tissue & Bone 6th ed. (Oct 2026) separates YAP1::TFE3 hemangioendothelioma as a distinct standalone entity (listed separately in this atlas).'
by_id['nm-ehe']['refs'].append('u_who6_stb')

by_id['s_gist']['pitfall'] += ' WHO 6th ed. Digestive and Soft Tissue & Bone (2026) separate SDH-deficient GIST as a distinct entity (listed separately in this atlas).'
by_id['s_gist']['refs'].extend(['u_who6_dig', 'u_who6_stb'])

by_id['v_intrahepatic_cholangiocarcinoma']['pitfall'] += ' WHO Digestive 6th ed. (July 2026) promotes small-duct and large-duct iCCA to separate entities (also listed separately in this atlas).'
by_id['v_intrahepatic_cholangiocarcinoma']['refs'].append('u_who6_dig')

by_id['v_invasive_lobular_carcinoma_of_breast']['pitfall'] += ' WHO Breast 6th ed. (2026) adds invasive lobular carcinoma with extracellular mucin (ILCEM), which shares biallelic CDH1 loss and 16q loss/1q gain but behaves more aggressively than pure mucinous carcinoma.'
by_id['v_invasive_lobular_carcinoma_of_breast']['refs'].extend(['u_who6_breast', 'u_ilcem'])

by_id['v_gastroblastoma']['rearr'] = ['Driver — MALAT1::GLI1 (characteristic) or PTCH1::GLI1; other GLI1 fusions reported']
by_id['v_gastroblastoma']['refs'].append('u_gli1')

by_id['v_colorectal_adenocarcinoma']['pitfall'] += ' WHO Digestive 6th ed. (2026) adds lymphoglandular complex-like adenocarcinoma (shares conventional CRC pathways, nested here), whereas IBD-associated IDH1-enriched low-grade tubuloglandular adenocarcinoma is listed separately.'
by_id['v_colorectal_adenocarcinoma']['refs'].append('u_who6_dig')

by_id['v_pancreatic_ductal_adenocarcinoma']['pitfall'] += ' Undifferentiated carcinoma with osteoclast-like giant cells shares core PDAC drivers (KRAS, TP53, CDKN2A, SMAD4) and is nested here; SWI/SNF-deficient undifferentiated GI/pancreatic carcinoma is listed separately.'
by_id['v_pancreatic_ductal_adenocarcinoma']['refs'].append('u_who6_dig')

by_id['e_swi']['pitfall'] += ' Includes SMARCB1-deficient sinonasal adenocarcinoma, a glandular variant with biallelic SMARCB1 loss and frequent yolk-sac-like or oncocytoid morphology.'
by_id['e_swi']['refs'].append('u_smarcb1_sin')

by_id['e_poro']['rearr'] = ['Driver — YAP1::NUTM1 or YAP1::MAML2; rare WWTR1::NUTM1']
by_id['e_poro']['refs'].append('u_skin_who5')

by_id['nm-fibro']['pitfall'] += ' Note: WHO Soft Tissue & Bone 6th ed. (Oct 2026) retired adult-type fibrosarcoma as a standalone category; retained here for historical differential context.'
by_id['nm-fibro']['refs'].append('u_who6_stb')

by_id['nm-ecto']['pitfall'] += ' Note: WHO Soft Tissue & Bone 6th ed. (Oct 2026) retired ectomesenchymoma as a standalone category; retained here for historical reference.'
by_id['nm-ecto']['refs'].append('u_who6_stb')

# Deduplicate refs while preserving order
for x in data['entities']:
    x['refs'] = list(dict.fromkeys(x['refs']))

ids = [x['id'] for x in data['entities']]
assert len(ids) == len(set(ids)), 'Duplicate entity ID'
assert len({x['name'] for x in data['entities']}) == len(ids), 'Duplicate name'
for x in data['entities']:
    for key in ['id', 'name', 'system', 'anchor', 'pitfall']:
        assert isinstance(x[key], str) and x[key].strip(), (x['id'], key)
    for key in ['snv', 'cnv', 'rearr', 'other', 'aliases', 'refs']:
        assert isinstance(x[key], list) and all(isinstance(v, str) for v in x[key]), (x['id'], key)
    assert x['refs'], x['id']
    assert all(k in data['sources'] for k in x['refs']), x['id']
for key, src in data['sources'].items():
    assert src['url'].startswith('https://'), key

order = list(dict.fromkeys(x['system'] for x in data['entities']))
data['entities'].sort(key=lambda x: order.index(x['system']))
data['reviewed'] = '2026-11-23'


def _stable_int_id(seed: str, base: int) -> int:
    digest = int(hashlib.sha256(seed.encode('utf-8')).hexdigest()[:10], 16)
    return base + (digest % 899_999_999_999)


def _anki_csum(first_field: str) -> int:
    plain = re.sub(r'<[^>]+>', '', first_field)
    plain = html_lib.unescape(plain)
    return int(hashlib.sha1(plain.encode('utf-8')).hexdigest()[:8], 16)


def _slug_tag(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')


def _fmt_list_html(items: list[str]) -> str:
    if not items:
        return '<span class="empty">No characteristic alteration summarized.</span>'
    lis = ''.join(f'<li>{html_lib.escape(s)}</li>' for s in items)
    return f'<ul>{lis}</ul>'


def build_apkg(atlas_data: dict, out_path: Path) -> int:
    """Generate a valid Anki 2.1 .apkg deck with subdecks by organ system using stdlib only."""
    now_sec = int(time.time())
    model_id = 1763894400101
    root_deck_id = 1763894400201
    sources = atlas_data['sources']

    systems = sorted({e['system'] for e in atlas_data['entities']})
    deck_ids = {sys_name: _stable_int_id(f'deck::{sys_name}', 1763894500000) for sys_name in systems}

    decks = {
        '1': {
            'id': 1, 'mod': now_sec, 'name': 'Default', 'usn': 0,
            'lrnToday': [0, 0], 'revToday': [0, 0], 'newToday': [0, 0], 'timeToday': [0, 0],
            'collapsed': False, 'browserCollapsed': False, 'desc': '', 'dyn': 0, 'conf': 1,
            'extendNew': 0, 'extendRev': 0,
        },
        str(root_deck_id): {
            'id': root_deck_id, 'mod': now_sec, 'name': 'Tumor Driver Atlas', 'usn': -1,
            'lrnToday': [0, 0], 'revToday': [0, 0], 'newToday': [0, 0], 'timeToday': [0, 0],
            'collapsed': False, 'browserCollapsed': False,
            'desc': f'Molecular pathology study deck ({len(atlas_data["entities"])} entries, reviewed {atlas_data["reviewed"]}).',
            'dyn': 0, 'conf': 1, 'extendNew': 0, 'extendRev': 0,
        },
    }
    for sys_name, did in deck_ids.items():
        decks[str(did)] = {
            'id': did, 'mod': now_sec, 'name': f'Tumor Driver Atlas::{sys_name}', 'usn': -1,
            'lrnToday': [0, 0], 'revToday': [0, 0], 'newToday': [0, 0], 'timeToday': [0, 0],
            'collapsed': False, 'browserCollapsed': False, 'desc': '', 'dyn': 0, 'conf': 1,
            'extendNew': 0, 'extendRev': 0,
        }

    card_css = (
        '.card{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
        'font-size:15px;line-height:1.55;color:#18212a;background:#f5f2ec;padding:20px;text-align:left;}'
        '.front{text-align:center;padding:28px 16px;background:#fff;border:1px solid #cec7b8;'
        'border-top:4px solid #791f32;border-radius:4px;}'
        '.eyebrow{font-family:"SFMono-Regular",Consolas,monospace;font-size:11px;'
        'letter-spacing:1.4px;text-transform:uppercase;color:#626765;margin-bottom:10px;}'
        '.entity{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;'
        'font-size:26px;line-height:1.2;margin:8px 0 14px;color:#18212a;}'
        '.prompt{font-size:13px;color:#626765;margin:0;}'
        '.cue{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;'
        'font-size:17px;line-height:1.4;background:#ebe6dc;border-left:3px solid #791f32;'
        'padding:10px 14px;margin:0 0 16px;}'
        '.sec{margin-bottom:12px;}'
        '.sec h3{font-family:"SFMono-Regular",Consolas,monospace;font-size:10px;'
        'letter-spacing:1px;text-transform:uppercase;margin:0 0 5px;}'
        '.snv{color:#791f32;}.cnv{color:#29586b;}.rearr{color:#45634d;}.other{color:#8c6422;}'
        '.sec ul{margin:0;padding-left:18px;font-size:13px;}'
        '.sec li{margin-bottom:4px;}'
        '.empty{font-size:12px;color:#626765;font-style:italic;}'
        '.pitfall{font-size:13px;margin:14px 0 12px;padding-top:10px;border-top:1px solid #cec7b8;}'
        '.pitfall b{color:#791f32;}'
        '.refs{font-size:11px;border-top:1px solid #cec7b8;padding-top:8px;}'
        '.refs a{display:block;color:#29586b;margin:3px 0;text-decoration:none;}'
        '.nightMode .card{background:#1c2128;color:#e6edf3;}'
        '.nightMode .front{background:#22272e;border-color:#444c56;border-top-color:#d46a7e;}'
        '.nightMode .entity{color:#e6edf3;}'
        '.nightMode .cue{background:#2d333b;border-left-color:#d46a7e;color:#e6edf3;}'
        '.nightMode .snv,.nightMode .pitfall b{color:#f08a9d;}'
        '.nightMode .cnv,.nightMode .refs a{color:#79c0ff;}'
        '.nightMode .rearr{color:#7ee787;}'
        '.nightMode .other{color:#e3b341;}'
        '.nightMode .eyebrow,.nightMode .prompt,.nightMode .empty{color:#8b949e;}'
        '.nightMode .pitfall,.nightMode .refs{border-top-color:#444c56;}'
    )

    qfmt = (
        '<div class="front">'
        '<div class="eyebrow">{{System}}</div>'
        '<div class="entity">{{Entity}}</div>'
        '<p class="prompt">Recall the key SNVs / indels, copy-number changes, rearrangements, and exceptions.</p>'
        '</div>'
    )
    afmt = (
        '{{FrontSide}}<hr id="answer">'
        '<div class="cue">{{Anchor}}</div>'
        '<div class="sec"><h3 class="snv">SNV / INDEL</h3>{{SNV}}</div>'
        '<div class="sec"><h3 class="cnv">COPY NUMBER</h3>{{CNV}}</div>'
        '<div class="sec"><h3 class="rearr">REARRANGEMENT</h3>{{Rearrangement}}</div>'
        '{{#Other}}<div class="sec"><h3 class="other">OTHER BIOLOGY</h3>{{Other}}</div>{{/Other}}'
        '<div class="pitfall"><b>Keep in mind · </b>{{Pitfall}}</div>'
        '{{#References}}<div class="refs">{{References}}</div>{{/References}}'
    )

    field_names = ['Entity', 'System', 'Anchor', 'SNV', 'CNV', 'Rearrangement', 'Other', 'Pitfall', 'References']
    flds = [
        {
            'name': fn, 'ord': idx, 'sticky': False, 'rtl': False,
            'font': 'Arial', 'size': 16, 'media': [],
        }
        for idx, fn in enumerate(field_names)
    ]

    models = {
        str(model_id): {
            'id': model_id, 'name': 'Tumor Driver Atlas', 'type': 0, 'mod': now_sec,
            'usn': -1, 'sortf': 0, 'did': root_deck_id,
            'tmpls': [{
                'name': 'Driver Recall', 'ord': 0, 'qfmt': qfmt, 'afmt': afmt,
                'bqfmt': '', 'bafmt': '', 'did': None, 'bfont': '', 'bsize': 0,
            }],
            'flds': flds, 'css': card_css, 'latexPre': '', 'latexPost': '',
            'latexsvg': False, 'req': [[0, 'any', [0]]], 'tags': [], 'vers': [],
        }
    }

    dconf = {
        '1': {
            'id': 1, 'mod': 0, 'name': 'Default', 'usn': 0, 'maxTaken': 60, 'autoplay': True,
            'timer': 0, 'replayq': True,
            'new': {'bury': False, 'delays': [1, 10], 'initialFactor': 2500, 'ints': [1, 4, 7], 'order': 1, 'perDay': 20},
            'rev': {'bury': False, 'ease4': 1.3, 'ivlFct': 1, 'maxIvl': 36500, 'perDay': 200, 'hardFactor': 1.2},
            'lapse': {'delays': [10], 'leechAction': 1, 'leechFails': 8, 'minInt': 1, 'mult': 0},
        }
    }
    conf = {
        'activeDecks': [root_deck_id], 'curDeck': root_deck_id, 'newSpread': 0,
        'collapseTime': 1200, 'timeLim': 0, 'estTimes': True, 'dueCounts': True,
        'curModel': str(model_id), 'nextPos': len(atlas_data['entities']) + 1,
        'sortType': 'noteFld', 'sortBackwards': False, 'addToCur': True,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'collection.anki2'
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.executescript('''
            CREATE TABLE col (
                id integer primary key, crt integer not null, mod integer not null,
                scm integer not null, ver integer not null, dty integer not null,
                usn integer not null, ls integer not null, conf text not null,
                models text not null, decks text not null, dconf text not null,
                tags text not null
            );
            CREATE TABLE notes (
                id integer primary key, guid text not null, mid integer not null,
                mod integer not null, usn integer not null, tags text not null,
                flds text not null, sfld text not null, csum integer not null,
                flags integer not null, data text not null
            );
            CREATE TABLE cards (
                id integer primary key, nid integer not null, did integer not null,
                ord integer not null, mod integer not null, usn integer not null,
                type integer not null, queue integer not null, due integer not null,
                ivl integer not null, factor integer not null, reps integer not null,
                lapses integer not null, left integer not null, odue integer not null,
                odid integer not null, flags integer not null, data text not null
            );
            CREATE TABLE revlog (
                id integer primary key, cid integer not null, usn integer not null,
                ease integer not null, ivl integer not null, lastIvl integer not null,
                factor integer not null, time integer not null, type integer not null
            );
            CREATE TABLE graves (usn integer not null, oid integer not null, type integer not null);
            CREATE INDEX ix_notes_usn ON notes (usn);
            CREATE INDEX ix_cards_usn ON cards (usn);
            CREATE INDEX ix_revlog_usn ON revlog (usn);
            CREATE INDEX ix_cards_nid ON cards (nid);
            CREATE INDEX ix_cards_sched ON cards (did, queue, due);
            CREATE INDEX ix_revlog_cid ON revlog (cid);
            CREATE INDEX ix_notes_csum ON notes (csum);
        ''')

        cur.execute(
            'INSERT INTO col VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (
                1, now_sec, now_sec * 1000, now_sec * 1000, 11, 0, 0, 0,
                json.dumps(conf, ensure_ascii=False),
                json.dumps(models, ensure_ascii=False),
                json.dumps(decks, ensure_ascii=False),
                json.dumps(dconf, ensure_ascii=False),
                '{}',
            ),
        )

        for idx, e in enumerate(atlas_data['entities'], start=1):
            nid = _stable_int_id(f'note::{e["id"]}', 1763895000000)
            cid = _stable_int_id(f'card::{e["id"]}', 1763896000000)
            guid = hashlib.sha256(f'tda::{e["id"]}'.encode('utf-8')).hexdigest()[:16]
            did = deck_ids[e['system']]

            other_html = ''.join(f'<p style="margin:3px 0">{html_lib.escape(s)}</p>' for s in e['other'])
            refs_html = ''.join(
                f'<a href="{html_lib.escape(sources[k]["url"])}">↗ {html_lib.escape(sources[k]["title"])}</a>'
                for k in e['refs'] if k in sources
            )
            fields = [
                html_lib.escape(e['name']),
                html_lib.escape(e['system']),
                html_lib.escape(e['anchor']),
                _fmt_list_html(e['snv']),
                _fmt_list_html(e['cnv']),
                _fmt_list_html(e['rearr']),
                other_html,
                html_lib.escape(e['pitfall']),
                refs_html,
            ]
            flds_str = '\x1f'.join(fields)
            sfld = e['name']
            csum = _anki_csum(fields[0])

            tags = ['tumor_driver_atlas', f'system::{_slug_tag(e["system"])}']
            for cls in ('snv', 'cnv', 'rearr', 'other'):
                if e[cls]:
                    tags.append(f'class::{cls}')
            tags_str = ' ' + ' '.join(tags) + ' '

            cur.execute(
                'INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (nid, guid, model_id, now_sec, -1, tags_str, flds_str, sfld, csum, 0, ''),
            )
            cur.execute(
                'INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (cid, nid, did, 0, now_sec, -1, 0, 0, idx, 0, 0, 0, 0, 0, 0, 0, 0, ''),
            )

        conn.commit()
        conn.close()

        with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(db_path, arcname='collection.anki2')
            zf.writestr('media', '{}')

    return out_path.stat().st_size


payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
template = (root / 'template.html').read_text(encoding='utf-8')
assert template.count('__DATA__') == 1
html = template.replace('__DATA__', payload)
(root.parent / 'index.html').write_text(html, encoding='utf-8')
(root / 'atlas.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
apkg_path = root.parent / 'tumor-driver-atlas.apkg'
apkg_bytes = build_apkg(data, apkg_path)

print(json.dumps({
    'entries': len(ids),
    'groups': len(order),
    'sources': len(data['sources']),
    'reviewed': data['reviewed'],
    'html_bytes': len(html.encode()),
    'apkg_bytes': apkg_bytes,
    'by_group': dict(Counter(x['system'] for x in data['entities'])),
}, indent=2))
