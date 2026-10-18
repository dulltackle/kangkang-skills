"""Exercise the acceptance-plan CLI with material completeness separate from semantic acceptance."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/acceptance_evidence.py'
class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def proof(self,name,value):
        p=self.root/name;p.write_text(json.dumps(value));return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    def call(self,manifest):
        p=self.root/'input.json';p.write_text(json.dumps(manifest))
        r=subprocess.run([sys.executable,str(SCRIPT),'--input',str(p),'--output',str(self.root/'plan.json')],text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr);return json.loads((self.root/'plan.json').read_text())
    def manifest(self):
        raw=self.proof('raw.json',dict(commit='abc',status='passed'))
        review=self.proof('review.json',dict(reviewer='R',implementer='A',commit='abc',criteria={'one':dict(text='Requirement one',decision='earned',reason='Verified the actual result',locations=['x:1'])}))
        return dict(ticket='demo#7',commit='abc',criteria=[dict(id='one',text='Requirement one',proofs=['run'])],
            proofs=[dict(id='run',**raw,commitPointer='/commit',statusPointer='/status',sources=[raw])],review=review)
    def test_plan_needs_matching_sources_and_independent_semantic_review(self):
        m=self.manifest();r=self.call(m)
        self.assertEqual(r['proposedCheckboxes'],{'one':True});self.assertFalse(r['written'])
        del m['review'];r=self.call(m)
        self.assertFalse(r['proposedCheckboxes']['one']);self.assertTrue(r['gaps'])
    def test_corruption_identity_and_unmapped_proof_fail_closed(self):
        for fault in ['hash','commit','mapping','source']:
            with self.subTest(fault=fault):
                m=self.manifest()
                if fault=='hash':m['proofs'][0]['sha256']='bad'
                if fault=='commit':m['commit']='def'
                if fault=='mapping':m['criteria'][0]['proofs']=[]
                if fault=='source':m['proofs'][0]['sources'][0]['path']=str(self.root/'missing')
                r=self.call(m);self.assertFalse(r['proposedCheckboxes']['one'])
    def test_reused_proof_keeps_original_identity_and_requires_explicit_content_match(self):
        m=self.manifest();m['commit']='def'
        m['review']=self.proof('new-review.json',dict(reviewer='R',implementer='A',commit='def',criteria={'one':dict(text='Requirement one',decision='earned',reason='Verified the original content',locations=['x:1'])}))
        m['proofs'][0]['reuse']=dict(originalCommit='abc',targetCommit='def',source=self.proof('reuse.json',dict(originalCommit='abc',targetCommit='def',unchanged=True,scope=['one'])))
        r=self.call(m);self.assertTrue(r['proposedCheckboxes']['one']);self.assertEqual(r['proofs'][0]['originalCommit'],'abc')
        del m['proofs'][0]['reuse'];self.assertFalse(self.call(m)['proposedCheckboxes']['one'])
if __name__=='__main__':unittest.main()
