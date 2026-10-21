import json
from pathlib import Path

sources = {}
entities = []
def source(key, title, url):
    sources[key] = dict(title=title, url=url)
def add(id, name, system, anchor, snv=(), cnv=(), rearr=(), other=(), pitfall='', refs=(), aliases=()):
    entities.append(dict(id=id, name=name, system=system, aliases=list(aliases), anchor=anchor,
                         snv=list(snv), cnv=list(cnv), rearr=list(rearr), other=list(other),
                         pitfall=pitfall, refs=list(refs)))

source('s_kit', 'Hirota et al. — KIT activation in GIST (1998)', 'https://pubmed.ncbi.nlm.nih.gov/9438854/')
source('s_pdgfra', 'Heinrich et al. — PDGFRA activation in GIST (2003)', 'https://pubmed.ncbi.nlm.nih.gov/12522257/')
source('s_wtgist', 'Boikos et al. — Molecular subtypes of KIT/PDGFRA wild-type GIST (2016)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5472100/')
source('s_ntrkgist', 'Cao et al. — NTRK-fusion GIST cohort (2022)', 'https://pubmed.ncbi.nlm.nih.gov/36612101/')
source('s_ntrkdiff', 'Suurmeijer et al. — GI NTRK-rearranged mesenchymal tumors and distinction from GIST (2021)', 'https://pubmed.ncbi.nlm.nih.gov/32669612/')
source('s_ppb', 'Pugh et al. — DICER1 and TP53 in pleuropulmonary blastoma (2014)', 'https://www.nature.com/articles/onc2014150')
source('s_ppms', 'Thway et al. — Primary pulmonary myxoid sarcoma (2011)', 'https://pubmed.ncbi.nlm.nih.gov/21997693/')
source('s_kaposi', 'Chang et al. — Discovery of KSHV in Kaposi sarcoma (1994)', 'https://pubmed.ncbi.nlm.nih.gov/7997879/')
source('s_kshv', 'IARC — Kaposi sarcoma herpesvirus: carcinogenicity evaluation', 'https://www.ncbi.nlm.nih.gov/books/NBK304348/')
source('s_gnet', 'Stockman et al. — Malignant gastrointestinal neuroectodermal tumor (2012)', 'https://pubmed.ncbi.nlm.nih.gov/22592145/')
source('s_eims', 'Lee et al. — ALK fusions in epithelioid inflammatory myofibroblastic sarcoma (2017)', 'https://pubmed.ncbi.nlm.nih.gov/27874193/')
source('s_uesl', 'Setty et al. — C19MC and TP53 in undifferentiated embryonal sarcoma of liver (2020)', 'https://pubmed.ncbi.nlm.nih.gov/32310940/')
source('s_dfsp', 'Abbott et al. — Fusion-copy gains in fibrosarcomatous DFSP (2006)', 'https://pubmed.ncbi.nlm.nih.gov/16980946/')
source('s_dfsp2', 'Lee et al. — PDGFB/PDGFD rearrangements in DFSP (2022)', 'https://pubmed.ncbi.nlm.nih.gov/35034038/')
source('s_pds', 'Griewank et al. — Mutations and copy-number profiles of pleomorphic dermal sarcoma (2018)', 'https://pubmed.ncbi.nlm.nih.gov/29099504/')

add('s_gist', 'Gastrointestinal stromal tumor', 'Soft tissue and bone',
    'GIST → KIT or PDGFRA; if neither, think SDH or RAS-pathway biology.',
    snv=['Driver — KIT activating SNVs/indels; alternative PDGFRA activating variants (including D842V)',
         'Alternative subsets — SDHA/B/C/D inactivation, NF1 loss, or BRAF activation'],
    rearr=['Rare reported subset — NTRK fusions; careful distinction from other GI mesenchymal tumors is essential'],
    other=['Alternative SDH-deficiency mechanism — SDHC promoter hypermethylation'],
    pitfall='KIT protein expression is not the same as a KIT mutation. Genotype alone does not determine metastatic risk. SDH/NF1 abnormalities may reflect germline predisposition; a tumor result alone does not establish this.',
    refs=['s_kit','s_pdgfra','s_wtgist','s_ntrkgist','s_ntrkdiff'], aliases=['GIST','malignant GIST'])
add('s_ppb', 'Pleuropulmonary blastoma', 'Thoracic',
    'Childhood pleuropulmonary blastoma → two DICER1 hits.',
    snv=['Driver — DICER1 loss-of-function plus an RNase IIIb hotspot missense mutation',
         'Progression/cooperating — TP53 inactivation; RAS-pathway lesions in subsets'],
    cnv=['Cooperating — TP53 allelic loss in a subset'],
    pitfall='The loss-of-function DICER1 hit is often germline but may be somatic. Types I–III are combined. Adult-type pulmonary blastoma is a different tumor; regressed type Ir is outside the malignant scope.',
    refs=['s_ppb'], aliases=['PPB'])
add('s_ppms', 'Primary pulmonary myxoid sarcoma', 'Thoracic',
    'Pulmonary myxoid sarcoma → EWSR1::CREB1.',
    rearr=['Characteristic — EWSR1::CREB1'],
    pitfall='This fusion is shared with other tumors, including GI neuroectodermal tumors and angiomatoid fibrous histiocytoma. Location and morphology remain essential.',
    refs=['s_ppms'])
add('s_kaposi', 'Kaposi sarcoma', 'Soft tissue and bone',
    'Kaposi sarcoma → KSHV / HHV8.',
    other=['Viral driver — Kaposi sarcoma-associated herpesvirus (KSHV / HHV8); viral latency and host signaling promote the neoplasm'],
    pitfall='A virally driven vascular neoplasm. No single recurrent human SNV, amplification or fusion is a defining study hallmark. Classic, endemic, epidemic and immunosuppression-associated settings are combined.',
    refs=['s_kaposi','s_kshv'], aliases=['KS','KSHV','HHV8'])
add('s_gnet', 'Malignant gastrointestinal neuroectodermal tumor', 'Soft tissue and bone',
    'GI neuroectodermal tumor → EWSR1 with ATF1 or CREB1.',
    rearr=['Characteristic — EWSR1::ATF1 or EWSR1::CREB1'],
    pitfall='Related fusion families occur in clear cell sarcoma, but this tumor lacks convincing melanocytic differentiation. An EWSR1 break-apart result does not by itself identify the partner or the diagnosis.',
    refs=['s_gnet'], aliases=['GNET','clear cell sarcoma-like tumor of gastrointestinal tract'])
add('s_eims', 'Epithelioid inflammatory myofibroblastic sarcoma', 'Soft tissue and bone',
    'Aggressive epithelioid IMT-family tumor → ALK fusion.',
    rearr=['Driver — RANBP2::ALK or RRBP1::ALK; other partners are reported'],
    pitfall='Included for its malignant behavior. Conventional inflammatory myofibroblastic tumor is an intermediate neoplasm and excluded from this atlas. ALK fusion alone does not establish this aggressive phenotype.',
    refs=['s_eims'], aliases=['EIMS'])
add('s_uesl', 'Undifferentiated embryonal sarcoma of liver', 'Digestive',
    'Embryonal liver sarcoma → C19MC activation plus TP53 damage.',
    snv=['Recurrent — TP53 inactivating variants'],
    cnv=['Cooperating — TP53 copy-number loss in a subset'],
    rearr=['Characteristic in molecular series — 19q13 structural rearrangements involving the C19MC microRNA region'],
    other=['Result — C19MC microRNA overexpression'],
    pitfall='A recurrent pattern from small molecular cohorts, not a required universal diagnostic criterion. C19MC involvement can also occur in its mesenchymal hamartoma precursor.',
    refs=['s_uesl'], aliases=['UESL'])
add('s_dfsp', 'Dermatofibrosarcoma protuberans, fibrosarcomatous', 'Soft tissue and bone',
    'Fibrosarcomatous DFSP retains PDGF-ligand fusion biology.',
    cnv=['Progression-associated — increased COL1A1::PDGFB fusion copy number in a subset'],
    rearr=['Characteristic — COL1A1::PDGFB',
           'Alternative subset — PDGFD fusions, including EMILIN2::PDGFD'],
    pitfall='Only the malignant fibrosarcomatous form is included. Conventional DFSP is intermediate. The fusion is shared with conventional DFSP and does not itself prove fibrosarcomatous transformation.',
    refs=['s_dfsp','s_dfsp2'], aliases=['DFSP','FS-DFSP','fibrosarcomatous dermatofibrosarcoma protuberans'])
add('s_pds', 'Pleomorphic dermal sarcoma', 'Skin & mucosal melanoma',
    'Pleomorphic dermal sarcoma → UV-related tumor-suppressor damage.',
    snv=['Recurrent — TP53, NOTCH1/2, FAT1, CDKN2A and TERT promoter alterations'],
    cnv=['Associated — complex gains and losses; no single defining copy-number signature'],
    other=['Associated — ultraviolet mutational signature'],
    pitfall='Substantial genetic overlap with atypical fibroxanthoma; depth, necrosis and invasive features distinguish the malignant phenotype. Atypical fibroxanthoma is outside the malignant-only scope.',
    refs=['s_pds'], aliases=['PDS'])

coverage = dict(systems=['Thoracic','Digestive','Soft tissue and bone','Skin & mucosal melanoma'],
    basis='Additional cross-system malignant entities checked against primary molecular studies.',
    merged=['PPB histologic types combined; conventional intermediate IMT and DFSP excluded while their aggressive sarcomatous counterparts are included.'],
    excluded=['Regressed PPB type Ir and atypical fibroxanthoma.'],
    limitations=['GIST genotype is not equivalent to metastatic behavior. The nosology of rare NTRK-fusion GI tumors requires careful pathological review.'])
Path(__file__).with_name('supplement.json').write_text(json.dumps(dict(sources=sources,entities=entities,coverage=coverage),ensure_ascii=False,indent=2), encoding='utf-8')
