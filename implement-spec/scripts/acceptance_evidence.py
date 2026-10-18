#!/usr/bin/env python3
"""Check configurable evidence and propose acceptance write-back; tracker operations, formal validation, and independent semantic review remain external."""
import argparse
import json
from pathlib import Path
import sys
from resources import digest, read_json, require, save


def verified(proof):
    require(isinstance(proof,dict) and Path(proof['path']).is_absolute(),'A source requires an absolute path and SHA-256')
    require(digest(proof['path'])==proof['sha256'],'Source missing or hash changed: '+proof['path'])
    return read_json(proof['path'])


def pointer(value, path):
    require(isinstance(path,str) and path.startswith('/'),'Specify a JSON Pointer into the original report')
    for token in path[1:].split('/'):
        key=token.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list) else value[key]
    return value


def plan(manifest):
    for key in ('ticket','commit'):
        require(isinstance(manifest.get(key),str) and manifest[key].strip(),'Missing: '+key)
    criteria=manifest['criteria']; proofs=manifest['proofs']
    require(criteria and len({c['id'] for c in criteria})==len(criteria),'Criteria must be nonempty and have unique IDs')
    require(len({p['id'] for p in proofs})==len(proofs),'Duplicate proof ID')
    require(all(isinstance(c.get('text'),str) and c['text'].strip() for c in criteria),'Criteria require their exact original text')
    gaps=[]; rows=[]; good={}
    for proof in proofs:
        row=dict(id=proof['id'],path=proof['path'],valid=False,reused=False)
        try:
            raw=verified(proof)
            require(proof.get('sources'),'Proofs must reference original sources')
            for source in proof['sources']:
                # Original sources may be text or binary; verify their hashes without requiring JSON.
                require(digest(source['path'])==source['sha256'],'Original source changed: '+source['path'])
            original=pointer(raw,proof['commitPointer']);row['originalCommit']=original
            require(pointer(raw,proof['statusPointer'])=='passed','The original report is not passed')
            if original!=manifest['commit']:
                reuse=proof.get('reuse',{})
                binding=verified(reuse['source'])
                require(reuse['originalCommit']==original==binding['originalCommit'] and
                    reuse['targetCommit']==manifest['commit']==binding['targetCommit'] and binding.get('unchanged') is True,
                    'Older evidence requires an explicit reuse record matching content and scope')
                needed={c['id'] for c in criteria if proof['id'] in c.get('proofs',[])}
                require(needed<=set(binding['scope']),'Reuse scope is insufficient')
                row['reused']=True;row['reuseSource']=reuse['source']
            row['valid']=True
        except (ValueError,OSError,KeyError,TypeError,IndexError) as e:
            gaps.append(dict(proof=proof['id'],reason=str(e)))
        rows.append(row);good[proof['id']]=row['valid']
    review=None
    try:
        review=verified(manifest['review'])
        require(review.get('reviewer') and review.get('implementer') and review['reviewer']!=review['implementer'],'The reviewer must be independent of the implementer')
        require(review['commit']==manifest['commit'],'Review commit mismatch')
    except (ValueError,OSError,KeyError,TypeError) as e:
        gaps.append(dict(review=True,reason=str(e)));review=None
    proposed={}
    for criterion in criteria:
        cid=criterion['id']; mapped=criterion.get('proofs',[])
        materials=bool(mapped) and len(set(mapped))==len(mapped) and all(good.get(pid,False) for pid in mapped)
        judgment=review.get('criteria',{}).get(cid,{}) if review else {}
        semantic=judgment.get('text')==criterion['text'] and judgment.get('decision')=='earned' and bool(judgment.get('reason')) and bool(judgment.get('locations'))
        proposed[cid]=materials and semantic
        if not materials:gaps.append(dict(criterion=cid,reason='Missing valid mappings or sources'))
        if not semantic:gaps.append(dict(criterion=cid,reason='Missing the current commit, exact criterion text, or independent semantic judgment'))
    mapped={pid for c in criteria for pid in c.get('proofs',[])}
    for pid in good:
        if pid not in mapped:gaps.append(dict(proof=pid,reason='Proof is not mapped to a criterion'))
    return dict(schemaVersion=1,ticket=manifest['ticket'],commit=manifest['commit'],proofs=rows,gaps=gaps,
        criteria=criteria,proposedCheckboxes=proposed,written=False,
        note='The plan checks commit, exact text, sources, and review declarations. Established formal validators check report completeness; reviewers judge semantics. Older evidence retains its original identity and time.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:
        require(a.input.resolve()!=a.output.resolve(),'Input and output paths must differ')
        result=plan(read_json(a.input));a.output.parent.mkdir(parents=True,exist_ok=True);save(a.output,result)
        print(json.dumps(dict(ticket=result['ticket'],earned=sum(result['proposedCheckboxes'].values()),total=len(result['criteria']),gaps=len(result['gaps']),written=False,plan=str(a.output.resolve())),ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(str(e),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
