"""Exercise shared budgets, offline recovery, and handoff decisions through the CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/workflow.py'

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def call(self, command, payload, ok=True):
        p = self.root/'input.json'; p.write_text(json.dumps(payload))
        r = subprocess.run([sys.executable,str(SCRIPT),'--state',str(self.root/'state.json'),'--run-id','test',command,'--input',str(p)],text=True,capture_output=True)
        self.assertEqual(r.returncode,0 if ok else 1,r.stderr)
        return json.loads(r.stdout) if ok else r
    def budget(self,event,minute,**kw):
        return self.call('budget',dict(phaseId='perf',event=event,at=f'2026-10-18T{minute//60:02}:{minute%60:02}:00Z',**kw))
    def state(self):
        return json.loads((self.root/'state.json').read_text())

    def proof(self, name='source.txt', text='Recorded evidence'):
        path = self.root/name; path.write_text(text)
        return str(path)

    def review(self, minute):
        return self.budget('review',minute,summary='Entry measurements show the parser is no longer the bottleneck.',
            nextAction='Profile the scheduler with the same complete entry point.',source=self.proof('review.txt'))

    def measure(self, minute, value, **kw):
        return self.budget('measure',minute,durationSeconds=value,source=self.proof(f'sample-{minute}.txt'),
            **dict(dict(completeEntry=True,comparisonKey='full/same-env'),**kw))

    def legacy(self, *, limit=45, explicit=False, pending=True, phased=False, continued=False, paused=False):
        start=dict(phaseId='perf',event='start',at='2026-10-18T00:00:00Z')
        if explicit: start['limitMinutes']=limit
        phase=dict(startedAt=start['at'],lastAt='2026-10-18T00:45:00Z',limitMinutes=limit,
            checkpointMinutes=30,pausedAt='2026-10-18T00:45:00Z' if paused else None,
            excludedSeconds=0,measurements=[],events=[start],decisionPending=pending)
        if phased or continued:
            choice='phase' if phased else 'continue'
            source=self.proof('user.txt','The user chose '+choice)
            phase['userDecision']=dict(choice=choice,source=dict(path=source,sha256='historical-hash'))
            phase['events'].append(dict(phaseId='perf',event='decide',at=phase['lastAt'],choice=choice,source=source))
            if phased: phase['phased']=True
        (self.root/'state.json').write_text(json.dumps(dict(schemaVersion=1,runId='test',budgets={'perf':phase},
            discovery={'untouched':True},handoffs=[{'untouched':True}])))
        return phase

    def test_autonomous_phase_excludes_wait_and_survives_handoff(self):
        self.budget('start',0)
        self.budget('pause',20,reason='user-wait')
        self.budget('resume',40)
        r=self.budget('status',50,actor='new-agent')
        self.assertEqual(r['elapsedMinutes'],30)
        self.assertEqual(r['decision'],'review')
        r=self.budget('status',65)
        self.assertTrue(r['newExperimentsAllowed'])
        self.assertFalse(r['decisionPending'])
        self.assertIsNone(r['limitMinutes'])
        self.assertEqual(r['allowedWork'],['repair','review','independent'])
        self.assertEqual(self.budget('start',66)['elapsedMinutes'],46)
        self.assertTrue(self.budget('status',180)['newExperimentsAllowed'])

    def test_periodic_review_is_acknowledged_without_resetting_history(self):
        self.budget('start',0)
        self.assertFalse(self.budget('status',29)['reviewDue'])
        self.assertEqual(self.budget('status',30)['reviewReasons'],['interval'])
        self.assertTrue(self.budget('status',31)['reviewDue'])
        r=self.review(32)
        self.assertFalse(r['reviewDue']);self.assertEqual(r['nextReviewMinutes'],62)
        self.assertFalse(self.budget('status',61)['reviewDue'])
        self.assertTrue(self.budget('status',62)['reviewDue'])
        self.assertEqual(len(self.state()['budgets']['perf']['reviews']),1)

    def test_low_gain_prompts_review_and_allows_experiments(self):
        self.budget('start',0)
        for minute,value in [(1,100),(2,98),(3,97)]: r=self.measure(minute,value)
        self.assertEqual(r['reviewReasons'],['low-gain'])
        self.assertEqual(r['decision'],'review');self.assertTrue(r['newExperimentsAllowed'])
        self.assertFalse(r['acceptanceChanged'])
        before=self.state()['budgets']['perf']['measurements']
        self.assertFalse(self.review(4)['reviewDue'])
        self.assertFalse(self.budget('status',5)['reviewDue'])
        self.assertEqual(self.state()['budgets']['perf']['measurements'],before)
        for minute,value in [(6,97),(7,98),(8,99)]: r=self.measure(minute,value)
        self.assertEqual(r['reviewReasons'],['low-gain'])
        self.assertEqual(len(self.state()['budgets']['perf']['measurements']),6)

    def test_incomparable_samples_break_the_low_gain_sequence(self):
        self.budget('start',0)
        self.measure(1,100)
        self.measure(2,99,completeEntry=False)
        self.assertFalse(self.measure(3,98)['reviewDue'])
        self.assertFalse(self.measure(4,97,comparisonKey='other-cache')['reviewDue'])
        self.assertFalse(self.measure(5,96)['reviewDue'])
        self.assertFalse(self.measure(6,95)['reviewDue'])
        self.assertTrue(self.measure(7,94)['reviewDue'])

    def test_user_budget_still_stops_and_requires_sourced_extension(self):
        source=self.proof('budget.txt','Spend at most 60 minutes.')
        self.budget('start',0,mode='bounded',limitMinutes=60,source=source)
        for minute,value in [(1,100),(2,98),(3,97)]: r=self.measure(minute,value)
        self.assertTrue(r['newExperimentsAllowed'])
        self.assertFalse(r['decisionPending'])
        r=self.budget('status',60)
        self.assertEqual(r['decision'],'tradeoff');self.assertFalse(r['newExperimentsAllowed'])
        self.assertFalse(self.review(61)['newExperimentsAllowed'])
        before=self.state()
        self.call('budget',dict(phaseId='perf',event='decide',at='2026-10-18T01:02:00Z',choice='continue',source=source),False)
        self.assertEqual(self.state(),before)
        r=self.budget('decide',62,choice='continue',extensionMinutes=20,source=self.proof('extension.txt','Add 20 minutes.'))
        self.assertEqual(r['limitMinutes'],80);self.assertTrue(r['newExperimentsAllowed'])
        self.assertEqual(len(self.state()['budgets']['perf']['measurements']),3)
        self.assertFalse(self.budget('status',80)['newExperimentsAllowed'])
        r=self.budget('decide',81,choice='autonomous',source=self.proof('autonomy.txt','Continue autonomously until acceptance.'))
        self.assertTrue(r['newExperimentsAllowed']);self.assertIsNone(r['limitMinutes'])

    def test_start_validates_explicit_budget_and_finite_numbers(self):
        source=self.proof()
        variants=[dict(limitMinutes=60),dict(mode='bounded',limitMinutes=60),dict(mode='bounded',limitMinutes=0,source=source),
            dict(mode='autonomous',limitMinutes=60),dict(checkpointMinutes=0),dict(checkpointMinutes=float('nan')),
            dict(limitMinutes=float('inf'),source=source),dict(checkpointMinutes=True),dict(mode='other')]
        for kw in variants:
            with self.subTest(kw=kw):
                self.call('budget',dict(phaseId='perf',event='start',at='2026-10-18T00:00:00Z',**kw),False)
                self.assertFalse((self.root/'state.json').exists())
        self.assertEqual(self.budget('start',0,limitMinutes=5,source=source)['mode'],'bounded')
        self.assertFalse(self.budget('status',5)['newExperimentsAllowed'])

    def test_pause_and_timestamp_validation_preserve_state(self):
        self.budget('start',0)
        self.assertFalse(self.budget('pause',10,reason='external-block')['newExperimentsAllowed'])
        before=self.state()
        for event,at,kw in [('pause','2026-10-18T00:11:00Z',{'reason':'user-wait'}),
            ('status','2026-10-18T00:09:00Z',{}),('status','2026-10-18T00:11:00',{})]:
            self.call('budget',dict(phaseId='perf',event=event,at=at,**kw),False)
            self.assertEqual(self.state(),before)
        self.assertEqual(self.budget('resume',50)['elapsedMinutes'],10)
        self.assertEqual(self.budget('status',70)['elapsedMinutes'],30)

    def test_legacy_default_gate_is_cleared_without_losing_evidence(self):
        old=self.legacy()
        data=self.state()
        samples=[dict(durationSeconds=value,comparisonKey='full/same-env',
            source=dict(path=self.proof(f'legacy-{value}.txt'),sha256=f'original-{value}')) for value in (100,98,97)]
        data['budgets']['perf']['measurements']=samples
        (self.root/'state.json').write_text(json.dumps(data))
        r=self.budget('status',60)
        self.assertEqual(r['mode'],'autonomous');self.assertTrue(r['newExperimentsAllowed'])
        self.assertFalse(r['decisionPending']);self.assertEqual(r['elapsedMinutes'],60)
        state=self.state();phase=state['budgets']['perf']
        self.assertEqual(phase['legacyBudget'],dict(limitMinutes=45,decisionPending=True))
        self.assertEqual(phase['events'][:-1],old['events'])
        self.assertEqual(phase['measurements'],samples)
        self.assertIn('low-gain',r['reviewReasons'])
        self.assertEqual(state['discovery'],{'untouched':True})
        self.assertEqual(state['handoffs'],[{'untouched':True}])
        self.assertTrue(self.budget('status',61)['newExperimentsAllowed'])

    def test_legacy_custom_limit_is_reconciled_from_saved_authorization(self):
        old=self.legacy(limit=60,explicit=True)
        r=self.budget('status',61)
        self.assertEqual(r['decision'],'reconcile');self.assertFalse(r['decisionPending'])
        self.assertFalse(r['newExperimentsAllowed'])
        r=self.budget('policy',62,mode='bounded',limitMinutes=60,source=self.proof('budget.txt','Stop after 60 minutes.'))
        self.assertEqual(r['decision'],'tradeoff')
        self.assertEqual(self.state()['budgets']['perf']['legacyBudget']['limitMinutes'],old['limitMinutes'])

    def test_legacy_limit_without_matching_start_provenance_is_ambiguous(self):
        self.legacy(limit=60)
        self.assertEqual(self.budget('status',61)['decision'],'reconcile')

    def test_legacy_forced_extension_can_adopt_autonomous_policy(self):
        old=self.legacy(limit=105,explicit=True,continued=True,paused=True)
        r=self.budget('status',61)
        self.assertEqual(r['decision'],'reconcile')
        r=self.budget('policy',62,mode='autonomous',source=self.proof('policy.txt','Continue autonomously; the earlier extension answered the old default gate.'))
        self.assertEqual(r['decision'],'paused');self.assertFalse(r['newExperimentsAllowed'])
        r=self.budget('resume',63)
        self.assertTrue(r['newExperimentsAllowed']);self.assertEqual(r['elapsedMinutes'],45)
        phase=self.state()['budgets']['perf']
        self.assertEqual(phase['userDecision'],old['userDecision'])
        self.assertEqual(phase['events'][:len(old['events'])],old['events'])
        self.assertIsNone(phase['limitMinutes'])

    def test_legacy_user_phase_choice_survives_policy_migration(self):
        self.legacy(phased=True)
        r=self.budget('status',60)
        self.assertEqual(r['decision'],'phased');self.assertFalse(r['newExperimentsAllowed'])
        r=self.budget('policy',61,mode='autonomous',source=self.proof('policy.txt','Use the autonomous policy.'))
        self.assertEqual(r['decision'],'phased');self.assertFalse(r['newExperimentsAllowed'])
        r=self.budget('decide',62,choice='continue',source=self.proof('resume.txt','Resume this phase.'))
        self.assertTrue(r['newExperimentsAllowed'])

    def test_user_phase_choice_can_be_resumed_with_authorization(self):
        self.budget('start',0)
        r=self.budget('decide',1,choice='phase',source=self.proof('phase.txt','Deliver this phase and stop experiments.'))
        self.assertEqual(r['decision'],'phased');self.assertFalse(r['newExperimentsAllowed'])
        r=self.budget('decide',2,choice='continue',source=self.proof('continue.txt','Continue the work.'))
        self.assertTrue(r['newExperimentsAllowed']);self.assertIsNone(r['limitMinutes'])

    def test_review_and_restart_cannot_weaken_a_budget(self):
        self.budget('start',0,mode='bounded',limitMinutes=5,source=self.proof('budget.txt'))
        self.assertFalse(self.budget('start',6)['newExperimentsAllowed'])
        before=self.state()
        for kw in [dict(event='start',mode='autonomous'),dict(event='policy',mode='autonomous'),
                   dict(event='policy',source=self.proof()),
                   dict(event='review',summary='Done',source=self.proof())]:
            self.call('budget',dict(phaseId='perf',at='2026-10-18T00:07:00Z',**kw),False)
            self.assertEqual(self.state(),before)
        self.assertFalse(self.review(7)['newExperimentsAllowed'])

    def test_handoff_blocks_active_checks_and_preserves_reviewer_during_repair(self):
        proof=self.root/'handoff.json';proof.write_text('{}')
        packet=dict(stage='functional',target='demo#42',commit='abc',contracts=['API stable'],
            unresolved=[],evidence=[str(proof)],activeChecks=['job1'],implementer='A',reviewer='R')
        self.call('handoff',packet,False)
        packet['activeChecks']=[]
        self.assertEqual(self.call('handoff',packet)['status'],'ready')
        packet.update(unresolved=['bug'],reviewer='R2')
        self.call('handoff',packet,False)
        packet['reviewer']='R'
        self.assertEqual(self.call('handoff',packet)['status'],'repair')
        packet.update(stage='acceptance',unresolved=[],implementer='B',reviewer='S',crossTicketReview=True)
        self.assertEqual(self.call('handoff',packet)['status'],'ready')

    def test_discovery_failure_only_preserves_preassigned_local_work(self):
        proof=self.root/'discovery.json';proof.write_text('{}')
        failed=dict(event='failed',source=str(proof))
        r=self.call('discovery',failed)
        self.assertEqual(r['localTickets'],[])
        snapshot=dict(event='snapshot',mode='full',scope='demo#42',tickets={'43':'a'},assigned=['43'],
            sources=[dict(name=n,complete=True,evidence=str(proof)) for n in ['native','bodies','dependencies']])
        self.call('discovery',snapshot)
        r=self.call('discovery',failed)
        self.assertEqual(r['localTickets'],['43'])
        self.assertFalse(r['dispatchAllowed']);self.assertFalse(r['writebackAllowed'])
        snapshot['tickets']['44']='b'
        r=self.call('discovery',snapshot)
        self.assertEqual(r['changedTickets'],['44'])
        self.assertFalse(r['integrationAllowed'])
        r=self.call('discovery',dict(event='reconciled',tickets=['44'],source=str(proof)))
        self.assertTrue(r['integrationAllowed'])
        r=self.call('discovery',dict(event='continuation'))
        self.assertTrue(r['dispatchAllowed'])
        self.assertFalse(r['writebackAllowed'])
        r=self.call('discovery',dict(event='gate',purpose='resume'))
        self.assertFalse(r['dispatchAllowed']);self.assertFalse(r['integrationAllowed'])
        r=self.call('discovery',dict(event='gate',purpose='handoff'))
        self.assertFalse(r['handoffAllowed'])
        self.call('discovery',snapshot)
        self.assertTrue(self.call('discovery',dict(event='gate',purpose='handoff'))['handoffAllowed'])

    def test_missing_snapshot_original_closes_reuse_gates(self):
        proof=self.root/'discovery.json';proof.write_text('{}')
        snapshot=dict(event='snapshot',mode='full',scope='demo#42',tickets={'43':'a'},assigned=['43'],
            sources=[dict(name=n,complete=True,evidence=str(proof)) for n in ['native','bodies','dependencies']])
        self.call('discovery',snapshot)
        proof.unlink()
        r=self.call('discovery',dict(event='gate',purpose='handoff'))
        self.assertFalse(r['dispatchAllowed']);self.assertFalse(r['handoffAllowed']);self.assertFalse(r['writebackAllowed'])
        self.assertEqual(r['localTickets'],[])
        self.assertTrue(r['sourceGaps'])
        proof.write_text('{"restored":true}')
        self.assertTrue(self.call('discovery',snapshot)['handoffAllowed'])

if __name__=='__main__': unittest.main()
