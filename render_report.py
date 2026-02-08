#!/usr/bin/env python3
import json, argparse, pathlib

ap=argparse.ArgumentParser()
ap.add_argument('--infile',required=True)
ap.add_argument('--out',default='council-report.md')
args=ap.parse_args()

j=json.loads(pathlib.Path(args.infile).read_text(encoding='utf-8'))

s=j.get('synthesis',{}).get('content','')
try:
    sj=json.loads(s)
except Exception:
    sj={"final_answer":s,"agreement_points":[],"disagreement_points":[],"risks":[],"open_questions":[],"next_actions":[],"confidence":0}

def bullets(items):
    if not items: return '- —'
    return '\n'.join([f'- {x}' for x in items])

md=[]
md.append('# Council Report')
md.append('')
md.append('## Query')
md.append(j.get('query',''))
md.append('')
md.append('## Final')
md.append(sj.get('final_answer',''))
md.append('')
md.append(f"**Confidence:** {round(float(sj.get('confidence',0))*100,1)}%")
md.append('')
md.append('## Agreement')
md.append(bullets(sj.get('agreement_points',[])))
md.append('')
md.append('## Disagreement')
md.append(bullets(sj.get('disagreement_points',[])))
md.append('')
md.append('## Risks')
md.append(bullets(sj.get('risks',[])))
md.append('')
md.append('## Open Questions')
md.append(bullets(sj.get('open_questions',[])))
md.append('')
md.append('## Next Actions')
md.append(bullets(sj.get('next_actions',[])))

pathlib.Path(args.out).write_text('\n'.join(md),encoding='utf-8')
print('Saved',args.out)
