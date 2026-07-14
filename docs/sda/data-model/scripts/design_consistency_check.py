from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs/sda/data-model'
model=json.loads((DM/'target-model.json').read_text())
errors=[]
# entity/dictionary/schema parity
schema=(DM/'draft-physical-schema.sql').read_text()
erd=(DM/'canonical-logical-erd.mmd').read_text()
dict_text=(DM/'data-dictionary.md').read_text()
for ent,fields in model['entities'].items():
    if f'proposed_{ent}' not in schema: errors.append(f'missing schema table {ent}')
    if ent.upper() not in erd: errors.append(f'missing ERD entity {ent}')
    for f in fields:
        if f not in dict_text: errors.append(f'missing dictionary field {ent}.{f}')
# vocab refs
vocab_text=(DM/'controlled-vocabularies.md').read_text()
for vocab,vals in model['vocabularies'].items():
    for val in vals:
        if val not in vocab_text: errors.append(f'missing vocabulary value {vocab}.{val}')
# representative records
reps=list((DM/'representative-records').glob('*.md'))
if len(reps)<7: errors.append('representative records < 7')
for p in reps:
    txt=p.read_text()
    for needle in ['location_record','location_record_version','geometry_observation','geometry_version','publication_release_item','Operator','Public']:
        if needle not in txt: errors.append(f'{p.name} missing {needle}')
# Mermaid and SQL cheap parse
if 'erDiagram' not in erd: errors.append('Mermaid ERD missing erDiagram')
if schema.count('(') != schema.count(')'): errors.append('SQL parentheses unbalanced')
if 'NON-EXECUTABLE DESIGN ARTIFACT' not in schema: errors.append('SQL non-executable marker missing')
if 'REFERENCES proposed_location_record' not in schema: errors.append('FK intent missing')
# ADR/RFI coverage
adrs=list((ROOT/'docs/sda/adrs').glob('ADR-00[5-9]*.md'))
rfis=list((ROOT/'docs/sda/rfis').glob('RFI-NLI-WO-002-*.md'))
if len(adrs)<5: errors.append('ADR coverage <5')
if len(rfis)<6: errors.append('RFI coverage <6')
# current field map completeness
catalog=(DM/'current-state-inventory.md').read_text()
fieldmap=(DM/'current-to-target-mapping.md').read_text()
current_fields=re.findall(r'`([a-zA-Z_][\w]*\.[a-zA-Z_][\w]*)`', fieldmap)
if len(set(current_fields)) < 120: errors.append(f'field map too small: {len(set(current_fields))}')
report=['# Design Consistency Report','',f'Generated checks: {9}',f'Errors: {len(errors)}','']
if errors:
    report += ['## Errors'] + [f'- {e}' for e in errors]
else:
    report += ['## PASS','- ERD/dictionary/schema entity coverage passed.','- FK intent and non-executable SQL lint passed.','- Vocabulary references passed.','- Representative-record structural checks passed.','- ADR/RFI coverage passed.','- Current-field map completeness threshold passed.','- Mermaid source contains `erDiagram`.','- SQL parentheses balanced.','- Classification and no-runtime evidence present.']
(DM/'design-consistency-report.md').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
sys.exit(1 if errors else 0)
