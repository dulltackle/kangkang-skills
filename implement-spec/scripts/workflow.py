#!/usr/bin/env python3
"""共享执行决策记录；不调度 agent，不修改 tracker，不产生语义验收结论。"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from resources import locked, save, read_json, require, evidence, digest


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None, '时间须含时区')
    return result


def budget(data, request):
    phases = data.setdefault('budgets', {})
    key, event, at = request['phaseId'], request['event'], stamp(request['at'])
    if key not in phases:
        require(event == 'start', '先建立共享阶段预算')
        limit = request.get('limitMinutes', 45)
        checkpoint = request.get('checkpointMinutes', min(30, limit))
        require(0 < checkpoint <= limit, '检查点与预算须为正数且检查点不晚于预算')
        phases[key] = dict(startedAt=request['at'], lastAt=request['at'], limitMinutes=limit,
                           checkpointMinutes=checkpoint, pausedAt=None, excludedSeconds=0,
                           measurements=[], events=[], decisionPending=False)
    phase = phases[key]
    require(at >= stamp(phase['lastAt']), '不能倒退共享时钟')
    if event == 'pause':
        require(request.get('reason') in ('user-wait', 'external-block'), '仅排除用户等待或明确外部阻塞')
        require(phase['pausedAt'] is None, '已有暂停')
        phase['pausedAt'] = request['at']
    elif event == 'resume':
        require(phase['pausedAt'] is not None, '没有暂停')
        phase['excludedSeconds'] += (at-stamp(phase['pausedAt'])).total_seconds()
        phase['pausedAt'] = None
    elif event == 'measure':
        require(request.get('durationSeconds', 0) > 0, '测量须为正数')
        # comparisonKey 固定完整入口/源码范围/模型/环境/冷热条件；非完整样本打断连续性。
        complete = request.get('completeEntry') is True
        comparison = request.get('comparisonKey') if complete else None
        require(not complete or isinstance(comparison, str) and comparison.strip(), '完整测量需要比较身份')
        phase['measurements'].append(dict(durationSeconds=request['durationSeconds'],
            comparisonKey=comparison, source=evidence(request['source'])))
    elif event == 'decide':
        require(phase['decisionPending'], '当前无待决取舍')
        require(request.get('choice') in ('continue', 'phase'), '需要明确继续或分期决定')
        phase['userDecision'] = dict(choice=request['choice'], source=evidence(request['source']))
        if request['choice'] == 'continue':
            extension=request.get('extensionMinutes',0)
            require(extension > 0, '继续需要明确追加预算')
            phase['limitMinutes'] += extension
            phase['measurements'] = []
            phase['decisionPending'] = False
        else:
            phase['phased'] = True
    else:
        require(event in ('start', 'status'), '未知预算事件')
    phase['events'].append(request)
    phase['lastAt'] = request['at']
    excluded = phase['excludedSeconds'] + ((at-stamp(phase['pausedAt'])).total_seconds() if phase['pausedAt'] else 0)
    elapsed = ((at-stamp(phase['startedAt'])).total_seconds()-excluded)/60
    samples=phase['measurements'][-3:]
    low = len(samples)==3 and samples[0]['comparisonKey'] is not None and len({x['comparisonKey'] for x in samples})==1 and all(
        (a['durationSeconds']-b['durationSeconds'])/a['durationSeconds'] < .05 for a,b in zip(samples,samples[1:]))
    if low or elapsed >= phase['limitMinutes'] or phase.get('phased'):
        phase['decisionPending'] = True
    decision = 'tradeoff' if phase['decisionPending'] else 'checkpoint' if elapsed>=phase['checkpointMinutes'] else 'continue'
    return dict(phaseId=key, elapsedMinutes=elapsed, limitMinutes=phase['limitMinutes'], decision=decision,
        newExperimentsAllowed=not phase['decisionPending'], allowedWork=['repair','review','independent'],
        acceptanceChanged=False, stateFile=None)


def handoff(data, request):
    for key in ('stage','target','commit','implementer','reviewer'):
        require(isinstance(request.get(key),str) and request[key].strip(),'交接缺少 '+key)
    for key in ('contracts','unresolved','evidence','activeChecks'):
        require(isinstance(request.get(key),list),'交接缺少列表 '+key)
    require(not request['activeChecks'],'原拥有者须收尾活动检查')
    history=data.setdefault('handoffs',[])
    previous=history[-1] if history else None
    if request['unresolved']:
        require(previous is not None and previous['reviewer']==request['reviewer'] and previous['stage']==request['stage'],
                '同问题修复循环保留 reviewer，并延后阶段交接')
    elif previous and previous['stage']!=request['stage']:
        require(previous['implementer']!=request['implementer'] and previous['reviewer']!=request['reviewer'],
                '主要阶段默认使用新实现/审查上下文；例外须单独记录用户决定')
    if request['stage']=='acceptance':
        require(request.get('crossTicketReview') is True,'最终审查须覆盖跨事项交互与缺口')
    packet=dict(request)
    packet['evidence']=[evidence(path) for path in request['evidence']]
    require(packet['evidence'],'交接须带证据索引')
    history.append(packet)
    return dict(status='repair' if request['unresolved'] else 'ready',packet=packet,
        note='接手者仍须独立判断来源可复用性；状态字段不证明实际 agent 独立性')


def discovery(data, request):
    state=data.setdefault('discovery',dict(snapshot=None,offline=True,pending=[],freshFull=False,events=[]))
    event=request['event']; changed=[]
    normalized=dict(request)
    if event in ('failed','reconciled'):
        normalized['source']=evidence(request['source'])
    if event=='failed':
        state['offline']=True;state['freshFull']=False
        evidence(request['source'])
    elif event=='snapshot':
        require(request.get('mode')=='full','增量覆盖未建立可验证协议时，使用完整分页快照')
        sources=request.get('sources',[])
        require({x['name'] for x in sources}=={'native','bodies','dependencies'} and len(sources)==3,'完整发现须核对全部关系/反向正文/依赖来源')
        for source in sources:
            require(source.get('complete') is True,'来源未完成；不能替代完整分页证明')
            evidence(source['evidence'])
        require(isinstance(request.get('tickets'),dict) and request['tickets'],'快照须包含父事项及完整条款/关系内容身份')
        require(set(request.get('assigned',[]))<=set(request['tickets']),'分配必须来自完整快照')
        normalized['sources']=[dict(source,evidence=evidence(source['evidence'])) for source in sources]
        old=state['snapshot']
        if old:
            require(old['scope']==request['scope'],'发现范围变化须建立新运行')
            changed=sorted(k for k in set(old['tickets'])|set(request['tickets']) if old['tickets'].get(k)!=request['tickets'].get(k))
        state.update(snapshot=normalized,offline=False,pending=sorted(set(state['pending'])|set(changed)),freshFull=True,
            currentProofs=[source['evidence'] for source in normalized['sources']])
    elif event=='reconciled':
        require(not state['offline'],'先恢复完整查询')
        evidence(request['source'])
        require(set(request['tickets'])<=set(state['pending']),'仅核对已知变化')
        state['pending']=[k for k in state['pending'] if k not in request['tickets']]
        state.setdefault('currentProofs',[]).append(normalized['source'])
    elif event=='continuation':
        require(state['snapshot'] is not None,'压缩续接不能替代首次完整发现')
        state['freshFull']=False
    elif event=='gate':
        require(request.get('purpose') in ('handoff','resume'),'未知核对边界')
        if request['purpose']=='resume':
            state['offline']=True;state['freshFull']=False
    else:
        raise ValueError('未知发现事件')
    state['events'].append(normalized)
    gaps=[]
    if state['snapshot'] and not state.get('currentProofs'):
        gaps.append('旧快照缺少来源哈希，需重新完整发现')
    for proof in state.get('currentProofs',[]):
        try:
            require(digest(proof['path'])==proof['sha256'],'来源变化: '+proof['path'])
        except (ValueError,OSError,KeyError,TypeError) as error:
            gaps.append(str(error))
    ready=state['snapshot'] is not None and not state['offline'] and not state['pending'] and not gaps
    return dict(localTickets=state['snapshot']['assigned'] if state['snapshot'] and not gaps else [],
        dispatchAllowed=ready,integrationAllowed=ready,writebackAllowed=ready and state['freshFull'],
        handoffAllowed=ready and state['freshFull'],changedTickets=changed,pending=state['pending'],sourceGaps=gaps,
        note='完整性字段是来源声明，协调者须核对分页及真实关系；本工具不查询 tracker')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=Path,required=True);p.add_argument('--run-id',required=True)
    p.add_argument('command',choices=['budget','handoff','discovery']);p.add_argument('--input',type=Path,required=True)
    a=p.parse_args()
    try:
        with locked(a.state):
            data=read_json(a.state) if a.state.exists() else dict(schemaVersion=1,runId=a.run_id)
            require(data.get('schemaVersion')==1 and data.get('runId')==a.run_id,'运行身份不符')
            result={'budget':budget,'handoff':handoff,'discovery':discovery}[a.command](data,read_json(a.input))
            save(a.state,data)
        result['stateFile']=str(a.state.resolve())
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(str(e),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
