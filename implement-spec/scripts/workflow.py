#!/usr/bin/env python3
"""Record shared execution decisions; scheduling, tracker writes, and semantic acceptance remain external."""
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys
from resources import locked, save, read_json, require, evidence, digest


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None, 'Timestamp must include a timezone')
    return result


def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def phase_policy(request):
    mode = request.get('mode', 'bounded' if request.get('limitMinutes') is not None else 'autonomous')
    require(mode in ('autonomous', 'bounded'), 'Choose autonomous or bounded mode')
    limit = request.get('limitMinutes')
    if mode == 'bounded':
        require(positive(limit), 'A user budget requires a positive finite limitMinutes')
        source = evidence(request['source'])
    else:
        require(limit is None, 'Autonomous mode has no time limit')
        source = evidence(request['source']) if 'source' in request else None
    return dict(mode=mode, limitMinutes=limit, policySource=source)


def migrate_phase(phase):
    if 'policyVersion' in phase:
        require(phase['policyVersion'] == 2, 'Unsupported phase policy version')
        return
    # Old numeric limits do not establish user intent. Preserve ambiguous choices for evidence-based reconciliation.
    starts = [e for e in phase['events'] if e['event'] == 'start']
    choices = [e for e in phase['events'] if e['event'] == 'decide']
    known_default = (phase.get('limitMinutes') == 45 and bool(starts)
                     and all('limitMinutes' not in e for e in starts) and not choices and not phase.get('userDecision'))
    phase['legacyBudget'] = {k: phase[k] for k in ('limitMinutes', 'decisionPending', 'userDecision') if k in phase}
    phase.update(policyVersion=2, mode='autonomous' if known_default else 'legacy',
                 limitMinutes=None, policySource=None, lastReviewMinutes=0,
                 reviewedMeasurements=0, reviews=[], decisionPending=bool(phase.get('phased')))


def phase_elapsed(phase, at):
    excluded = phase['excludedSeconds']
    if phase['pausedAt']:
        excluded += (at-stamp(phase['pausedAt'])).total_seconds()
    return ((at-stamp(phase['startedAt'])).total_seconds()-excluded)/60


def budget(data, request):
    phases = data.setdefault('budgets', {})
    key, event, at = request['phaseId'], request['event'], stamp(request['at'])
    if key not in phases:
        require(event == 'start', 'Start the shared performance phase first')
        policy = phase_policy(request)
        checkpoint = request.get('checkpointMinutes', 30)
        require(positive(checkpoint), 'The review interval must be positive and finite')
        phases[key] = dict(startedAt=request['at'], lastAt=request['at'],
                           checkpointMinutes=checkpoint, pausedAt=None, excludedSeconds=0,
                           measurements=[], events=[], decisionPending=False, policyVersion=2,
                           lastReviewMinutes=0, reviewedMeasurements=0, reviews=[], **policy)
    phase = phases[key]
    require(at >= stamp(phase['lastAt']), 'Shared timestamps must be monotonic')
    migrate_phase(phase)
    if event == 'policy':
        require(request.get('mode') in ('autonomous', 'bounded'), 'A policy update requires an explicit mode')
        proof = evidence(request['source'])
        phase.update(phase_policy(request), policySource=proof)
    elif event == 'pause':
        require(request.get('reason') in ('user-wait', 'external-block'), 'Exclude only user waits or explicit external blocks')
        require(phase['pausedAt'] is None, 'The phase is already paused')
        phase['pausedAt'] = request['at']
    elif event == 'resume':
        require(phase['pausedAt'] is not None, 'The phase is not paused')
        phase['excludedSeconds'] += (at-stamp(phase['pausedAt'])).total_seconds()
        phase['pausedAt'] = None
    elif event == 'measure':
        require(positive(request.get('durationSeconds')), 'Measurement duration must be positive and finite')
        # comparisonKey fixes entry point, source scope, model, environment, cache state, and concurrency.
        complete = request.get('completeEntry') is True
        comparison = request.get('comparisonKey') if complete else None
        require(not complete or isinstance(comparison, str) and comparison.strip(), 'A complete measurement requires a comparison identity')
        phase['measurements'].append(dict(durationSeconds=request['durationSeconds'],
            comparisonKey=comparison, source=evidence(request['source'])))
    elif event == 'review':
        require(all(isinstance(request.get(k), str) and request[k].strip() for k in ('summary', 'nextAction')),
                'A review requires findings and a concrete next action')
        phase['reviews'].append(dict(at=request['at'], summary=request['summary'],
            nextAction=request['nextAction'], source=evidence(request['source'])))
        phase['lastReviewMinutes'] = phase_elapsed(phase, at)
        phase['reviewedMeasurements'] = len(phase['measurements'])
    elif event == 'decide':
        choice = request.get('choice')
        require(choice in ('continue', 'autonomous', 'phase'), 'Choose continue, autonomous, or phase')
        require(phase['mode'] != 'legacy' or choice == 'phase', 'Reconcile the legacy policy from saved authorization first')
        elapsed = phase_elapsed(phase, at)
        pending = phase.get('phased') or phase['mode'] == 'bounded' and elapsed >= phase['limitMinutes']
        require(pending or choice == 'phase', 'There is no pending user budget or phased-delivery decision')
        proof = evidence(request['source'])
        if choice == 'continue' and phase['mode'] == 'bounded':
            extension = request.get('extensionMinutes')
            require(positive(extension), 'Continuing a user budget requires an explicit positive finite extensionMinutes')
            phase['limitMinutes'] += extension
        elif choice == 'autonomous':
            phase.update(mode='autonomous', limitMinutes=None, policySource=proof)
        phase['userDecision'] = dict(choice=choice, source=proof)
        phase['phased'] = choice == 'phase'
    else:
        require(event in ('start', 'status'), 'Unknown budget event')
        if event == 'start':
            require(all(k not in request or request[k] == phase.get(k)
                        for k in ('mode', 'limitMinutes', 'checkpointMinutes')),
                    'Use policy to change an existing phase; start preserves its state')
    phase['events'].append(request)
    phase['lastAt'] = request['at']
    elapsed = phase_elapsed(phase, at)
    samples = phase['measurements'][phase['reviewedMeasurements']:][-3:]
    low = len(samples) == 3 and samples[0]['comparisonKey'] is not None and len({x['comparisonKey'] for x in samples}) == 1 and all(
        (a['durationSeconds']-b['durationSeconds'])/a['durationSeconds'] < .05 for a,b in zip(samples,samples[1:]))
    reasons = []
    if elapsed >= phase['lastReviewMinutes'] + phase['checkpointMinutes']:
        reasons.append('interval')
    if low:
        reasons.append('low-gain')
    expired = phase['mode'] == 'bounded' and elapsed >= phase['limitMinutes']
    phase['decisionPending'] = bool(expired or phase.get('phased'))
    decision = ('phased' if phase.get('phased') else 'reconcile' if phase['mode'] == 'legacy'
                else 'tradeoff' if expired else 'paused' if phase['pausedAt'] else 'review' if reasons else 'continue')
    return dict(phaseId=key, elapsedMinutes=elapsed, mode=phase['mode'], limitMinutes=phase['limitMinutes'],
        decision=decision, decisionPending=phase['decisionPending'], reviewDue=bool(reasons), reviewReasons=reasons,
        nextReviewMinutes=phase['lastReviewMinutes']+phase['checkpointMinutes'],
        newExperimentsAllowed=not phase['decisionPending'] and phase['mode'] != 'legacy' and phase['pausedAt'] is None,
        allowedWork=['repair','review','independent'], acceptanceChanged=False, stateFile=None)


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
