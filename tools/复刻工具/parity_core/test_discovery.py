import unittest
import discover
import report

SPEC = {"openapi":"3.0.3","paths":{
    "/users":{"get":{"operationId":"listUsers","summary":"List users"},"post":{"summary":"Create user"}},
    "/users/{id}":{"get":{"summary":"Get user"},"delete":{"summary":"Delete user"}}
}}

class DiscoveryTests(unittest.TestCase):
    def test_all_api_methods_discovered(self):
        matrix = discover.discover(SPEC)
        self.assertEqual(matrix["feature_count"], 4)
    def test_only_safe_paths_planned(self):
        p=discover.read_only_plan(discover.discover(SPEC))
        self.assertEqual(len(p["cases"]), 1)
        self.assertEqual(p["cases"][0]["path"],"/users")
        self.assertEqual(len(p["excluded"]), 3)
    def test_unknown_implementation(self):
        self.assertTrue(all(x["implementation"]=="UNKNOWN" for x in discover.discover(SPEC)["features"]))
    def test_invalid_spec_rejected(self):
        with self.assertRaises(ValueError):
            discover.discover({"paths":[]})
    def test_report_never_claims_whole_product_rate(self):
        matrix=discover.discover(SPEC)
        result={"results":[{"id":matrix["features"][0]["id"],"pass":True}]}
        out=report.summarize(matrix,result)
        self.assertEqual(out["whole_software_recreation_rate"],"UNKNOWN")
        self.assertEqual(out["known_features"],4)
        self.assertEqual(out["not_verified"],3)
    def test_report_rejects_unknown_id(self):
        with self.assertRaises(ValueError):
            report.summarize(discover.discover(SPEC),{"results":[{"id":"fake","pass":True}]})

if __name__=="__main__":
    unittest.main()
