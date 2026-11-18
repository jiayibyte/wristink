"""Merge the reviewed zh/en copy and the 26 translations into the store files, then validate.

- store-listings/copies.json: Moke and Retro World, 28 locales (title kept as published).
- alpine/store/localizations.json: Alpine, 28 locales (title kept; headline/tagline/demoCaption for banners).
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = json.loads((HERE / 'copy-zh-en.json').read_text(encoding='utf-8'))
LOCALES = ['zh_TW', 'zh_CN', 'ja', 'in', 'ms', 'cs', 'da', 'de', 'en', 'es', 'fr', 'hr', 'it', 'hu', 'nl', 'nb', 'pl',
           'pt_BR', 'pt_PT', 'sk', 'sl', 'fi', 'sv', 'el', 'ru', 'iw', 'th', 'ko']


def load(app):
    out = {}
    for part in ('a', 'b'):
        out.update(json.loads((HERE / 'i18n' / f'{app}-{part}.json').read_text(encoding='utf-8')))
    return out


def check(app, key, entry, version):
    assert 0 < len(entry['title']) <= 50, (app, key, 'title', len(entry['title']))
    for field in ('description', 'whatsNew'):
        text = entry[field]
        assert 0 < len(text) <= 4000, (app, key, field, len(text))
        for bad in ('TODO', 'TBD', 'TRANSLATE', '�'):
            assert bad not in text, (app, key, field, bad)
    assert entry['whatsNew'].split('\n')[0] == version, (app, key, entry['whatsNew'][:12])
    assert '--' in entry['description'], (app, key, 'missing -- note')


def main():
    report = {}
    copies_path = REPO / 'store-listings/copies.json'
    copies = json.loads(copies_path.read_text(encoding='utf-8'))
    for app, src_key in (('moke', 'moke'), ('retro-world', 'retro')):
        tr = load(src_key)
        version = SRC[app]['version']
        assert set(tr) | {'zh_CN', 'en'} == set(LOCALES), (app, set(LOCALES) ^ (set(tr) | {'zh_CN', 'en'}))
        for key in LOCALES:
            entry = copies[app][key]
            new = SRC[app][key] if key in ('zh_CN', 'en') else tr[key]
            entry['description'] = new['description']
            entry['whatsNew'] = new['whatsNew']
            check(app, key, entry, version)
        report[app] = {k: (len(copies[app][k]['description']), len(copies[app][k]['whatsNew'])) for k in LOCALES}
    copies_path.write_text(json.dumps(copies, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    loc_path = REPO / 'alpine/store/localizations.json'
    loc = json.loads(loc_path.read_text(encoding='utf-8'))
    tr = load('alpine')
    version = SRC['alpine']['version']
    assert set(tr) | {'zh_CN', 'en'} == set(LOCALES)
    for key in LOCALES:
        entry = loc[key]
        new = SRC['alpine'][key] if key in ('zh_CN', 'en') else tr[key]
        for field in ('description', 'whatsNew', 'headline', 'tagline', 'demoCaption'):
            entry[field] = new[field]
        check('alpine', key, entry, version)
    loc_path.write_text(json.dumps(loc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report['alpine'] = {k: (len(loc[k]['description']), len(loc[k]['whatsNew'])) for k in LOCALES}
    (HERE / 'i18n' / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    for app, rows in report.items():
        longest = max(rows.items(), key=lambda kv: kv[1][0])
        print(f'{app}: {len(rows)} locales ok; longest description {longest[0]} {longest[1][0]} chars')


if __name__ == '__main__':
    main()
