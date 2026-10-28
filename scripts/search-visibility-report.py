#!/usr/bin/env python3
"""Summarize bounded search exports locally; never fetches or fabricates data."""
import argparse,csv,json,math,hashlib
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
AI_DOMAINS={'chatgpt.com':'chatgpt','chat.openai.com':'chatgpt','perplexity.ai':'perplexity','gemini.google.com':'gemini','copilot.microsoft.com':'copilot','claude.ai':'claude'}
def classify(value):
 value=(value or '').strip().lower()
 try:host=urlparse(value if '://' in value else '//'+value).hostname or ''
 except ValueError:return 'unknown'
 for domain,platform in AI_DOMAINS.items():
  if host==domain or host.endswith('.'+domain):return platform
 return 'other_or_unattributed'
def classify_event(row):
 details=row.get('details') or {}
 if isinstance(details,str):
  try:details=json.loads(details)
  except (ValueError,TypeError):details={}
 hashed=row.get('referrer_hash') or (details.get('referrer_host_sha256') if isinstance(details,dict) else None)
 if hashed:
  for domain,platform in AI_DOMAINS.items():
   for host in [domain,'www.'+domain]:
    if hashlib.sha256(('tct-lane4-public-referrer-host-v1|'+host).encode()).hexdigest()==hashed:return platform
 return classify(row.get('referrer_host') or row.get('utm_source') or '')
def read_rows(path):
 if path.stat().st_size>10_000_000:raise ValueError('Export exceeds 10 MB limit')
 if path.suffix=='.csv':
  with path.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
 else:
  data=json.loads(path.read_text());rows=data if isinstance(data,list) else data.get('events',data.get('rows',[]))
 if not isinstance(rows,list) or len(rows)>100000 or any(not isinstance(r,dict) for r in rows):raise ValueError('Expected at most 100000 objects')
 return rows
def summarize(search_rows=None,event_rows=None):
 report={'search':{'status':'missing_export','quick_win_candidates':None},'ai_referrals':{'status':'missing_export','event_counts_by_platform':None},'limits':['Referrer information can be absent. Events are observations, not unique people, citations, calls, sales or revenue.','Search position averages vary by country, device and query; an average is not a guaranteed rank.']}
 if search_rows is not None:
  eligible=invalid=0
  for row in search_rows:
   r={k.strip().lower():v for k,v in row.items()}
   try:
    pos=float(r['position']);imp=float(r['impressions'])
    if not math.isfinite(pos) or not math.isfinite(imp) or pos<0 or imp<0:raise ValueError()
    eligible+=int(8<=pos<=20 and imp>0)
   except (KeyError,ValueError,TypeError):invalid+=1
  report['search']={'status':'summarized','rows':len(search_rows),'invalid_rows':invalid,'quick_win_candidates':eligible}
 if event_rows is not None:
  counts=Counter();qa=0
  for r in event_rows:
   if r.get('tct_attribution_test') or r.get('controlled_test_run_id') or r.get('test_run_id') or r.get('traffic_kind') == 'controlled_test' or r.get('is_test') is True:qa+=1;continue
   # Do not output URLs, paths, query text, identifiers or individual event bodies.
   counts[classify_event(r)]+=1
  report['ai_referrals']={'status':'summarized','rows':len(event_rows),'excluded_test_rows':qa,'event_counts_by_platform':dict(counts)}
 return report
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--search-export',type=Path);parser.add_argument('--events-export',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 result=summarize(read_rows(args.search_export) if args.search_export else None,read_rows(args.events_export) if args.events_export else None)
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':'report_written','search':result['search']['status'],'ai_referrals':result['ai_referrals']['status']}))
if __name__=='__main__':main()
