import sys,os,re,yaml,shutil,datetime
from liquid import Environment, FileSystemLoader
src,out=sys.argv[1],sys.argv[2]
cfg=yaml.safe_load(open(f'{src}/_config.yml',encoding='utf-8'))
data={f[:-4]:yaml.safe_load(open(f'{src}/_data/{f}',encoding='utf-8')) for f in os.listdir(f'{src}/_data')}
site=dict(cfg,data=data,time=datetime.datetime.now())
env=Environment(loader=FileSystemLoader(f'{src}/_includes'))
env.add_filter('relative_url',lambda s:s)
def fm(path):
    t=open(path,encoding='utf-8').read(); m=re.match(r'---\n(.*?)\n---\n(.*)',t,re.S); return yaml.safe_load(m.group(1)),m.group(2)
layout=re.sub(r'{% include (\S+) %}',r'{% include "\1" %}',open(f'{src}/_layouts/default.html',encoding='utf-8').read())
shutil.rmtree(out+"/assets",ignore_errors=True)
shutil.copytree(f'{src}/assets',f'{out}/assets',ignore=shutil.ignore_patterns('.omc'))
files=[]
for root,ds,fs in os.walk(src):
    ds[:]=[d for d in ds if not d.startswith(('_','.')) and d!='assets']
    for f in fs:
        if not f.endswith('.html'): continue
        full=os.path.join(root,f)
        if not open(full,encoding='utf-8').read().startswith('---'):
            rel=os.path.relpath(full,src); os.makedirs(os.path.dirname(os.path.join(out,rel)),exist_ok=True); shutil.copy(full,os.path.join(out,rel)); continue
        files.append(full)
for f in files:
    meta,body=fm(f)
    url=meta.get('permalink','/'); meta['url']=url
    content=env.from_string(body).render(site=site,page=meta)
    html=content if meta.get('layout') in (None,'null',False) else env.from_string(layout).render(site=site,page=meta,content=content)
    # make links work from file:// by pointing to index.html
    d=out+url; os.makedirs(d,exist_ok=True)
    open(d+'index.html','w',encoding='utf-8').write(html); print('built',url)
