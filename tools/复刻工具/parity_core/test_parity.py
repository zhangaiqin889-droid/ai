import unittest
from unittest.mock import patch
import parity

class ParityTests(unittest.TestCase):
    def test_equal_responses(self):
        self.assertTrue(parity.compare({"status": 200, "json": {"a": 1}}, {"status": 200, "json": {"a": 1}}, "x")["pass"])
    def test_different_response_fails(self):
        self.assertFalse(parity.compare({"status": 200}, {"status": 500}, "x")["pass"])
    def test_blocks_http(self):
        with self.assertRaises(ValueError):
            parity.verify_target("http://a.example", ["a.example"])
    def test_blocks_other_host(self):
        with self.assertRaises(ValueError):
            parity.verify_target("https://a.example", ["b.example"])
    def test_blocks_credentials(self):
        with self.assertRaises(ValueError):
            parity.verify_target("https://u:p@a.example", ["a.example"])
    def test_blocks_write_method(self):
        with self.assertRaises(ValueError):
            parity.fetch("https://a.example", {"path": "/", "method": "POST"}, ["a.example"])
    def test_blocks_cross_host_path(self):
        with self.assertRaises(ValueError):
            parity.fetch("https://a.example", {"path": "//b.example"}, ["a.example"])
    def test_empty_cases_rejected(self):
        with self.assertRaises(ValueError):
            parity.run_plan({"cases": []}, "https://a.example", "https://b.example", ["a.example", "b.example"])
    def test_duplicate_ids_rejected(self):
        with patch.object(parity, "fetch", return_value={"status": 200, "json": {}}):
            with self.assertRaises(ValueError):
                parity.run_plan({"cases": [{"id": "a", "path": "/"}, {"id": "a", "path": "/"}]}, "https://a.example", "https://b.example", ["a.example", "b.example"])
    def test_end_to_end_plan_dispatch(self):
        with patch.object(parity, "fetch", side_effect=[
            {"status": 200, "json": {"x": 1}}, {"status": 200, "json": {"x": 1}},
            {"status": 200, "json": {"x": 2}}, {"status": 200, "json": {"x": 3}}
        ]):
            result = parity.run_plan({"cases": [{"id": "one", "path": "/one"}, {"id": "two", "path": "/two"}]},
                                     "https://a.example", "https://b.example", ["a.example", "b.example"])
        self.assertEqual((result["passed"], result["total"]), (1, 2))

if __name__ == "__main__":
    unittest.main()
