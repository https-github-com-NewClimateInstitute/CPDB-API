import unittest

from cpdb_api.request import Request


class RequestBaselineTests(unittest.TestCase):
    def test_string_formatting(self):
        r = Request()
        r.add_policy_instruments(["a b c", "hello"])
        r.marshal()
        self.assertEqual("a b c,hello", r._properties["policy_instruments"])

    def test_request(self):
        r = Request()
        r.set_country("Germany")
        r.set_decision_date("2021")
        r.set_status("Draft")
        r.add_sectors(["agriculture and forestry", "CCS"])
        r.add_policy_instruments(["grid access and priority for renewables", "strategic planning"])
        r.add_mitigation_areas(["energy efficiency"])
        r.marshal()
        want = dict({"country": "Germany", "decision_date": "2021", "status": "draft",
                     "sectors": "agriculture and forestry,CCS",
                     "policy_instruments": "grid access and priority for renewables,strategic planning",
                     "mitigation_areas": "energy efficiency"})
        self.assertEqual(r._properties, want)


if __name__ == '__main__':
    unittest.main()
