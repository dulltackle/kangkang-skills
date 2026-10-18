#!/usr/bin/env python3
"""核对配置化证据并生成验收写回计划；不访问 tracker，不代替专业校验器或独立语义审查。"""
import argparse
import json
from pathlib import Path
import sys
from resources import digest, read_json, require, save


def verified(proof):
    require(isinstance(proof,dict) and Path(proof['path']).is_absolute(),'来源须为绝对路径及 SHA256')
    require(digest(proof['path'])==proof['sha256'],'来源缺失或哈希变化: '+proof['path'])
    return read_json(proof['path'])


def pointer(value, path):
    require(isinstance(path,str) and path.startswith('/'),'指定原报告 JSON Pointer')
    for token in path[1:].split('/'):
        key=token.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list) else value[key]
    return value


def plan(manifest):
    for key in ('ticket','commit'):
        require(isinstance(manifest.get(key),str) and manifest[key].strip(),'缺少 '+key)
    criteria=manifest['criteria']; proofs=manifest['proofs']
    require(criteria and len({c['id'] for c in criteria})==len(criteria),'条款不能为空或重复')
    require(len({p['id'] for p in proofs})==len(proofs),'证据 ID 重复')
    require(all(isinstance(c.get('text'),str) and c['text'].strip() for c in criteria),'条款须含准确原文')
    gaps=[]; rows=[]; good={}
    for proof in proofs:
        row=dict(id=proof['id'],path=proof['path'],valid=False,reused=False)
        try:
            raw=verified(proof)
            require(proof.get('sources'),'证据须关联原始来源')
            for source in proof['sources']:
                # 原始来源可以是文本/二进制，核对内容摘要而非强制 JSON。
                require(digest(source['path'])==source['sha256'],'原始来源变化: '+source['path'])
            original=pointer(raw,proof['commitPointer']);row['originalCommit']=original
            require(pointer(raw,proof['statusPointer'])=='passed','原报告不是 passed')
            if original!=manifest['commit']:
                reuse=proof.get('reuse',{})
                binding=verified(reuse['source'])
                require(reuse['originalCommit']==original==binding['originalCommit'] and
                    reuse['targetCommit']==manifest['commit']==binding['targetCommit'] and binding.get('unchanged') is True,
                    '旧证据须有内容/范围匹配的显式复用记录')
                needed={c['id'] for c in criteria if proof['id'] in c.get('proofs',[])}
                require(needed<=set(binding['scope']),'复用范围不足')
                row['reused']=True;row['reuseSource']=reuse['source']
            row['valid']=True
        except (ValueError,OSError,KeyError,TypeError,IndexError) as e:
            gaps.append(dict(proof=proof['id'],reason=str(e)))
        rows.append(row);good[proof['id']]=row['valid']
    review=None
    try:
        review=verified(manifest['review'])
        require(review.get('reviewer') and review.get('implementer') and review['reviewer']!=review['implementer'],'审查者须独立于实现者')
        require(review['commit']==manifest['commit'],'审查提交不匹配')
    except (ValueError,OSError,KeyError,TypeError) as e:
        gaps.append(dict(review=True,reason=str(e)));review=None
    proposed={}
    for criterion in criteria:
        cid=criterion['id']; mapped=criterion.get('proofs',[])
        materials=bool(mapped) and len(set(mapped))==len(mapped) and all(good.get(pid,False) for pid in mapped)
        judgment=review.get('criteria',{}).get(cid,{}) if review else {}
        semantic=judgment.get('text')==criterion['text'] and judgment.get('decision')=='earned' and bool(judgment.get('reason')) and bool(judgment.get('locations'))
        proposed[cid]=materials and semantic
        if not materials:gaps.append(dict(criterion=cid,reason='缺少有效映射/来源'))
        if not semantic:gaps.append(dict(criterion=cid,reason='缺少当前提交、准确条款原文及独立语义判断'))
    mapped={pid for c in criteria for pid in c.get('proofs',[])}
    for pid in good:
        if pid not in mapped:gaps.append(dict(proof=pid,reason='证据未映射到条款'))
    return dict(schemaVersion=1,ticket=manifest['ticket'],commit=manifest['commit'],proofs=rows,gaps=gaps,
        criteria=criteria,proposedCheckboxes=proposed,written=False,
        note='计划只核对提交、原文、来源及审查声明；既有正式验收校验器负责原报告完整性，reviewer 负责语义真实性。旧证据保留原身份/时间。')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:
        require(a.input.resolve()!=a.output.resolve(),'不得覆盖输入')
        result=plan(read_json(a.input));a.output.parent.mkdir(parents=True,exist_ok=True);save(a.output,result)
        print(json.dumps(dict(ticket=result['ticket'],earned=sum(result['proposedCheckboxes'].values()),total=len(result['criteria']),gaps=len(result['gaps']),written=False,plan=str(a.output.resolve())),ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(str(e),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
