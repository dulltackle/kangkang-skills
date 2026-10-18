#!/usr/bin/env python3
"""Record shared execution decisions; scheduling, tracker writes, and semantic acceptance remain external."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from resources import locked, save, read_json, require, evidence, digest


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None, 'Timestamp must include a timezone')
    return result


def budget(data, request):
    phases = data.setdefault('budgets', {})
    key, event, at = request['phaseId'], request['event'], stamp(request['at'])
    if key not in phases:
        require(event == 'start', 'Start the shared phase budget first')
        limit = request.get('limitMinutes', 45)
        checkpoint = request.get('checkpointMinutes', min(30, limit))
        require(0 < checkpoint <= limit, 'Budget and checkpoint must be positive, with the checkpoint within the budget')
        phases[key] = dict(startedAt=request['at'], lastAt=request['at'], limitMinutes=limit,
                           checkpointMinutes=checkpoint, pausedAt=None, excludedSeconds=0,
                           measurements=[], events=[], decisionPending=False)
    phase = phases[key]
    require(at >= stamp(phase['lastAt']), 'Shared timestamps must be monotonic')
    if event == 'pause':
        require(request.get('reason') in ('user-wait', 'external-block'), 'Exclude only user waits or explicit external blocks')
        require(phase['pausedAt'] is None, 'The phase is already paused')
        phase['pausedAt'] = request['at']
    elif event == 'resume':
        require(phase['pausedAt'] is not None, 'The phase is not paused')
        phase['excludedSeconds'] += (at-stamp(phase['pausedAt'])).total_seconds()
        phase['pausedAt'] = None
    elif event == 'measure':
        require(request.get('durationSeconds', 0) > 0, 'Measurement duration must be positive')
        # comparisonKey fixes entry point, source scope, model, environment, and cache state; incomplete samples break the sequence.
        complete = request.get('completeEntry') is True
        comparison = request.get('comparisonKey') if complete else None
        require(not complete or isinstance(comparison, str) and comparison.strip(), 'A complete measurement requires a comparison identity')
        phase['measurements'].append(dict(durationSeconds=request['durationSeconds'],
            comparisonKey=comparison, source=evidence(request['source'])))
    elif event == 'decide':
        require(phase['decisionPending'], 'There is no pending tradeoff decision')
        require(request.get('choice') in ('continue', 'phase'), 'Choose explicitly between continuing and phased delivery')
        phase['userDecision'] = dict(choice=request['choice'], source=evidence(request['source']))
        if request['choice'] == 'continue':
            extension=request.get('extensionMinutes',0)
            require(extension > 0, 'Continuing requires an explicit budget extension')
            phase['limitMinutes'] += extension
            phase['measurements'] = []
            phase['decisionPending'] = False
        else:
            phase['phased'] = True
    else:
        require(event in ('start', 'status'), 'Unknown budget event')
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
        require(isinstance(request.get(key),str) and request[key].strip(),'Handoff is missing: '+key)
    for key in ('contracts','unresolved','evidence','activeChecks'):
        require(isinstance(request.get(key),list),'Handoff is missing list: '+key)
    require(not request['activeChecks'],'The original owner must close out active checks')
    history=data.setdefault('handoffs',[])
    previous=history[-1] if history else None
    if request['unresolved']:
        require(previous is not None and previous['reviewer']==request['reviewer'] and previous['stage']==request['stage'],
                'Retain the reviewer through the same issue repair loop and defer stage handoff')
    elif previous and previous['stage']!=request['stage']:
        require(previous['implementer']!=request['implementer'] and previous['reviewer']!=request['reviewer'],
                'Major stages default to fresh implementation and review contexts; record user-decided exceptions separately')
    if request['stage']=='acceptance':
        require(request.get('crossTicketReview') is True,'Final review must cover cross-ticket interactions and gaps')
    packet=dict(request)
    packet['evidence']=[evidence(path) for path in request['evidence']]
    require(packet['evidence'],'Handoff requires an evidence index')
    history.append(packet)
    return dict(status='repair' if request['unresolved'] else 'ready',packet=packet,
        note='The receiver independently assesses evidence reuse; status fields do not prove actual agent independence')


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
        require(request.get('mode')=='full','Use a fully paginated snapshot until incremental coverage has a verifiable protocol')
        sources=request.get('sources',[])
        require({x['name'] for x in sources}=={'native','bodies','dependencies'} and len(sources)==3,'Complete discovery requires native relationships, reverse body links, and dependency sources')
        for source in sources:
            require(source.get('complete') is True,'The source is incomplete; full pagination evidence is required')
            evidence(source['evidence'])
        require(isinstance(request.get('tickets'),dict) and request['tickets'],'The snapshot must include the parent and complete criterion and relationship content identities')
        require(set(request.get('assigned',[]))<=set(request['tickets']),'Assignments must come from the complete snapshot')
        normalized['sources']=[dict(source,evidence=evidence(source['evidence'])) for source in sources]
        old=state['snapshot']
        if old:
            require(old['scope']==request['scope'],'A discovery scope change requires a new run')
            changed=sorted(k for k in set(old['tickets'])|set(request['tickets']) if old['tickets'].get(k)!=request['tickets'].get(k))
        state.update(snapshot=normalized,offline=False,pending=sorted(set(state['pending'])|set(changed)),freshFull=True,
            currentProofs=[source['evidence'] for source in normalized['sources']])
    elif event=='reconciled':
        require(not state['offline'],'Restore complete queries first')
        evidence(request['source'])
        require(set(request['tickets'])<=set(state['pending']),'Reconcile only known changes')
        state['pending']=[k for k in state['pending'] if k not in request['tickets']]
        state.setdefault('currentProofs',[]).append(normalized['source'])
    elif event=='continuation':
        require(state['snapshot'] is not None,'Context continuation cannot replace first complete discovery')
        state['freshFull']=False
    elif event=='gate':
        require(request.get('purpose') in ('handoff','resume'),'Unknown reconciliation boundary')
        if request['purpose']=='resume':
            state['offline']=True;state['freshFull']=False
    else:
        raise ValueError('Unknown discovery event')
    state['events'].append(normalized)
    gaps=[]
    if state['snapshot'] and not state.get('currentProofs'):
        gaps.append('The legacy snapshot lacks source hashes; repeat complete discovery')
    for proof in state.get('currentProofs',[]):
        try:
            require(digest(proof['path'])==proof['sha256'],'Source changed: '+proof['path'])
        except (ValueError,OSError,KeyError,TypeError) as error:
            gaps.append(str(error))
    ready=state['snapshot'] is not None and not state['offline'] and not state['pending'] and not gaps
    return dict(localTickets=state['snapshot']['assigned'] if state['snapshot'] and not gaps else [],
        dispatchAllowed=ready,integrationAllowed=ready,writebackAllowed=ready and state['freshFull'],
        handoffAllowed=ready and state['freshFull'],changedTickets=changed,pending=state['pending'],sourceGaps=gaps,
        note='Completeness fields are source declarations; the coordinator verifies pagination and relationships through the tracker')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=Path,required=True);p.add_argument('--run-id',required=True)
    p.add_argument('command',choices=['budget','handoff','discovery']);p.add_argument('--input',type=Path,required=True)
    a=p.parse_args()
    try:
        with locked(a.state):
            data=read_json(a.state) if a.state.exists() else dict(schemaVersion=1,runId=a.run_id)
            require(data.get('schemaVersion')==1 and data.get('runId')==a.run_id,'Run identity mismatch')
            result={'budget':budget,'handoff':handoff,'discovery':discovery}[a.command](data,read_json(a.input))
            save(a.state,data)
        result['stateFile']=str(a.state.resolve())
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(str(e),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
