"""Prepare a focused Instinct 3 Solar build without regenerating other targets."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
NS={'iq':'http://www.garmin.com/xml/connectiq'}
ET.register_namespace('iq',NS['iq'])
folder=ROOT/'build/instinct3'
folder.mkdir(parents=True,exist_ok=True)
for demo in (False,True):
    tree=ET.parse(ROOT/('preview/manifest.xml' if demo else 'manifest.xml'))
    products=tree.getroot().find('iq:application/iq:products',NS)
    for item in list(products):
        if item.get('id')!='instinct3solar45mm':products.remove(item)
    name='preview' if demo else 'live'
    tree.write(folder/(name+'-manifest.xml'),encoding='utf-8',xml_declaration=True)
    (folder/(name+'.jungle')).write_text('project.manifest = '+name+'-manifest.xml\nbase.sourcePath = ../../source;../../'+('preview' if demo else 'live')+';../../profiles/base\nbase.resourcePath = ../../resources'+(';../../preview/resources' if demo else '')+'\nbase.lang.eng = ../../resources-eng\n')
print('Prepared Instinct 3 Solar 45/50mm target (two part-number variants).')
