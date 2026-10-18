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
    def test_shared_budget_excludes_wait_and_survives_handoff(self):
        self.budget('start',0)
        self.budget('pause',20,reason='user-wait')
        self.budget('resume',40)
        r=self.budget('status',50,actor='new-agent')
        self.assertEqual(r['elapsedMinutes'],30)
        self.assertEqual(r['decision'],'checkpoint')
        r=self.budget('status',65)
        self.assertEqual(r['decision'],'tradeoff')
        self.assertFalse(r['newExperimentsAllowed'])
        self.assertEqual(r['allowedWork'],['repair','review','independent'])
        self.assertEqual(self.budget('start',66)['decision'],'tradeoff')

    def test_low_gain_requires_three_comparable_full_measurements_and_user_override(self):
        self.budget('start',0,limitMinutes=60,checkpointMinutes=25)
        source=self.root/'measurement.json';source.write_text('{}')
        for minute,value in [(1,100),(2,98),(3,97)]:
            r=self.budget('measure',minute,durationSeconds=value,completeEntry=True,comparisonKey='full/same-env',source=str(source))
        self.assertEqual(r['decision'],'tradeoff')
        source.write_text('The user explicitly adds 20 minutes')
        r=self.budget('decide',4,choice='continue',extensionMinutes=20,source=str(source))
        self.assertEqual(r['limitMinutes'],80)
        self.assertTrue(r['newExperimentsAllowed'])
        for minute,value in [(5,100),(6,99),(7,98)]:
            r=self.budget('measure',minute,durationSeconds=value,completeEntry=False,source=str(source))
        self.assertNotEqual(r['decision'],'tradeoff')

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
