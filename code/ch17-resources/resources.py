"""Resource observations distinguish measured zero, unknown and query error."""
import argparse,json
from datetime import datetime,timezone

def observation(value,status,source,query,error=None,ids=None):
    return dict(value=value,status=status,source=source,query=query,
        checked_utc=datetime.now(timezone.utc).isoformat(),error=error,ids=ids)

def network_errors():
    """Exceptions that mean 'the query failed': huggingface_hub 1.x raises httpx errors, 2.x httpx2 errors."""
    from huggingface_hub.errors import HfHubHTTPError
    errors=[HfHubHTTPError]
    for name in ('httpx','httpx2'):
        try:errors.append(__import__(name).HTTPError)
        except ImportError:pass
    return tuple(errors)

def hub_count(api,kind,aliases):
    if not aliases:return observation(None,'not_checked','Hugging Face Hub',[])
    ids=set()
    try:
        for alias in aliases:
            if kind=='models':items=api.list_models(filter=alias)
            elif kind=='datasets':items=api.list_datasets(language=alias)
            else:raise ValueError('kind must be models or datasets')
            ids.update(item.id for item in items)
    except network_errors() as exc:
        return observation(None,'error','Hugging Face Hub',aliases,error=str(exc))
    return observation(len(ids),'observed','Hugging Face Hub',aliases,ids=sorted(ids))

def main():
    from huggingface_hub import HfApi
    p=argparse.ArgumentParser();p.add_argument('--iso3',required=True);p.add_argument('--hub-alias',action='append',default=[])
    p.add_argument('--output',required=True);a=p.parse_args();api=HfApi()
    result={'iso3':a.iso3,'models':hub_count(api,'models',a.hub_alias),
        'datasets':hub_count(api,'datasets',a.hub_alias),
        'ud':observation(None,'not_checked','UD release inventory',None),
        'fst_quality':observation(None,'not_checked','requires held-out gold evaluation',None),
        'wikipedia':observation(None,'not_checked','MediaWiki siteinfo statistics; edition code must be verified',None)}
    with open(a.output,'w') as f:json.dump(result,f,indent=2)
if __name__=='__main__':main()
