#!/usr/bin/env python3
import os, json, time, subprocess

KEY = os.environ['PRINTFUL_API_KEY']; SID = '18449429'
BASE = 'https://api.printful.com'
OUT = '/tmp/claude-0/-home-user-6Sylence/8c3fcd3b-97f5-5eba-8dbb-55d25d700afa/scratchpad'
LOG = open(os.path.join(OUT, 'mockups.log'), 'a')
def log(*a):
    m=' '.join(str(x) for x in a); LOG.write(m+'\n'); LOG.flush(); print(m)

EMB   = 'https://cdn.shopify.com/s/files/1/1003/6874/4832/files/marqueteria-emblem.png?v=1784593923'
EMBSQ = 'https://cdn.shopify.com/s/files/1/1003/6874/4832/files/marqueteria-emblem-sq.png?v=1784594206'
AOP   = 'https://cdn.shopify.com/s/files/1/1003/6874/4832/files/marqueteria-aop-xl.jpg?v=1784594207'

def pos(w,h): return {"area_width":w,"area_height":h,"width":w,"height":h,"top":0,"left":0}

SPECS = [
 {"key":"tee","pid":71,"variant":4017,"files":[{"placement":"front","image_url":EMB,"position":pos(1800,2400)}]},
 {"key":"crew","pid":145,"variant":5435,"files":[{"placement":"front","image_url":EMB,"position":pos(1800,2400)}]},
 {"key":"hoodie","pid":380,"variant":10780,"files":[{"placement":"front","image_url":EMBSQ,"position":pos(1800,1800)}]},
 {"key":"mhigh","pid":513,"variant":17458,"files":[
     {"placement":"shoe_quarters_left","image_url":AOP,"position":pos(2250,2250)},
     {"placement":"shoe_quarters_right","image_url":AOP,"position":pos(2250,2250)},
     {"placement":"shoe_tongue_left","image_url":AOP,"position":pos(2250,2250)},
     {"placement":"shoe_tongue_right","image_url":AOP,"position":pos(2250,2250)}]},
 {"key":"wslip","pid":575,"variant":14731,"files":[
     {"placement":"shoe_left","image_url":AOP,"position":pos(2325,2325)},
     {"placement":"shoe_right","image_url":AOP,"position":pos(2325,2325)}]},
 {"key":"bandana","pid":630,"variant":16032,"files":[{"placement":"front","image_url":AOP,"position":pos(4125,4125)}]},
]

def curl(method, path, body=None):
    args=['curl','-sS','--max-time','60','-X',method,BASE+path,
          '-H','Authorization: Bearer '+KEY,'-H','X-PF-Store-Id: '+SID]
    if body is not None:
        args+=['-H','Content-Type: application/json','-d',json.dumps(body)]
    r=subprocess.run(args,capture_output=True,text=True)
    try: return json.loads(r.stdout)
    except Exception: return {"code":-1,"raw":r.stdout[:300]}

def create_task(spec):
    for attempt in range(8):
        d=curl('POST',f"/mockup-generator/create-task/{spec['pid']}",
               {"variant_ids":[spec["variant"]],"format":"jpg","files":spec["files"]})
        c=d.get('code')
        if c==200:
            return d['result']['task_key']
        if c==429:
            msg=str(d.get('result',''))
            wait=51
            for tok in msg.split():
                if tok.isdigit(): wait=int(tok); break
            log(spec['key'],'429 wait',wait); time.sleep(wait+3); continue
        log(spec['key'],'create ERR',json.dumps(d)[:300]); return None
    return None

def poll(task_key, key):
    for _ in range(40):
        time.sleep(11)
        d=curl('GET',f"/mockup-generator/task?task_key={task_key}")
        st=d.get('result',{}).get('status') if d.get('code')==200 else None
        if st=='completed':
            return d['result'].get('mockups',[])
        if st=='failed':
            log(key,'task FAILED',json.dumps(d)[:300]); return None
        log(key,'status',st)
    log(key,'poll timeout'); return None

results={}
for i,spec in enumerate(SPECS):
    log('=== create',spec['key'])
    tk=create_task(spec)
    if not tk:
        results[spec['key']]={"error":"create_failed"};
    else:
        mocks=poll(tk,spec['key'])
        urls=[]
        for m in (mocks or []):
            if m.get('mockup_url'): urls.append(m['mockup_url'])
            for ex in m.get('extra',[]) or []:
                if ex.get('url'): urls.append(ex['url'])
        results[spec['key']]={"task_key":tk,"urls":urls}
        log(spec['key'],'got',len(urls),'mockups')
    json.dump(results, open(os.path.join(OUT,'mockups.json'),'w'), indent=1)
    if i < len(SPECS)-1:
        time.sleep(62)  # respect create-task rate limit
log('DONE')
json.dump(results, open(os.path.join(OUT,'mockups.json'),'w'), indent=1)
