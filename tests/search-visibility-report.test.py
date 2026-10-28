import importlib.util,unittest,hashlib
from pathlib import Path
spec=importlib.util.spec_from_file_location('report',Path(__file__).parents[1]/'scripts/search-visibility-report.py');report=importlib.util.module_from_spec(spec);spec.loader.exec_module(report)
class Reporting(unittest.TestCase):
 def test_missing_is_not_zero(self):
  result=report.summarize();self.assertIsNone(result['search']['quick_win_candidates']);self.assertIsNone(result['ai_referrals']['event_counts_by_platform'])
 def test_positions_and_test_exclusion(self):
  result=report.summarize([{'Position':12,'Impressions':100},{'Position':float('nan'),'Impressions':10}], [{'referrer_host':'chatgpt.com'},{'referrer_host':'chatgpt.com.attacker.example'},{'referrer_host':'www.perplexity.ai','is_test':True}])
  self.assertEqual(result['search']['quick_win_candidates'],1);self.assertEqual(result['search']['invalid_rows'],1)
  self.assertEqual(result['ai_referrals']['event_counts_by_platform'],{'chatgpt':1,'other_or_unattributed':1});self.assertEqual(result['ai_referrals']['excluded_test_rows'],1)
 def test_durable_hash_and_controlled_qa(self):
  value=hashlib.sha256(b"tct-lane4-public-referrer-host-v1|chatgpt.com").hexdigest()
  result=report.summarize(event_rows=[{"details":{"referrer_host_sha256":value}},{"traffic_kind":"controlled_test","test_run_id":"synthetic"}])
  self.assertEqual(result["ai_referrals"]["event_counts_by_platform"],{"chatgpt":1})
  self.assertEqual(result["ai_referrals"]["excluded_test_rows"],1)
 def test_domain_boundaries(self):
  self.assertEqual(report.classify('https://gemini.google.com/private?token=secret'),'gemini')
  self.assertEqual(report.classify('evilchatgpt.com'),'other_or_unattributed')
if __name__=='__main__':unittest.main()
