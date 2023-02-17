import unittest
import pandas as pd
import requests
import os

_API_URL = os.getenv("API_URL")
_username = os.getenv("API_USER")
_password = os.getenv("API_PASSWORD")

class RequestBaselineTests(unittest.TestCase):

    def set_api_request(self):
        r = Request()
        r.set_api_user(_username)
        r.set_api_password(_password)
        return r

    def test_string_formatting(self):
        r = Request()
        r.add_policy_instrument(["a b c", "hello"])
        r.marshal()
        self.assertEqual("a b c,hello", r._properties["policy_instrument"])

    def test_request(self):
        r = Request()
        r.set_country("Germany")
        r.set_decision_date("2021")
        r.set_policy_status("Draft")
        r.add_sector(["agriculture and forestry", "CCS"])
        r.add_policy_instrument(["grid access and priority for renewables", "strategic planning"])
        r.add_policy_type(["energy efficiency"])
        r.marshal()
        want = dict({"country_iso": "Germany", "decision_date": "2021", "policy_status": "draft",
                     "sector": "agriculture and forestry,CCS",
                     "policy_instrument": "grid access and priority for renewables,strategic planning",
                     "policy_type": "energy efficiency"})
        self.assertEqual(r._properties, want)
      
    def test_filter_country(self):
        r = self.set_api_request()
        want = "IND"
        r.set_country(want)
        got = r.issue()["country_iso"].unique()[0]
        self.assertEqual(want, got, "Incorrect country filter value")
    
    def test_filter_decision_date(self):
        r = self.set_api_request()
        want = "2018"
        r.set_decision_date(want)
        got = r.issue()["decision_date"].unique()[0]
        self.assertEqual(want, got, "Incorrect decision date filter value")
    
    def test_filter_policy_status(self):
        r = self.set_api_request()
        want = "In force"
        r.set_policy_status(want)
        got = r.issue()["policy_status"].unique()[0]
        self.assertEqual(want, got, "Incorrect implement state filter value")
    
    def test_filter_sector(self):
        r = self.set_api_request()
        want = "Transport"
        r.add_sector([want])
        got = r.issue()["sector"].unique()
        # Sector is a repeated field.
        for value in got:
          self.assertTrue(want in value, "Incorrect sector filter value")

    def test_filter_policy_instrument(self):
        r = self.set_api_request()
        p1 = "Grid access and priority for renewables"
        p2 = "Policy support"
        want = p1 + "," + p2
        r.add_policy_instrument([want])
        got = r.issue()["policy_instrument"].unique()
        for value in got:
          self.assertTrue(p1 in value or p2 in value, "Incorrect policy instrument value")

    def test_filter_policy_type(self):
        r = self.set_api_request()
        p1 = "Energy efficiency"
        p2 = "Renewables"
        want = p1 + "," + p2
        r.add_policy_type([want])
        got = r.issue()["policy_type"].unique()
        for value in got:
          self.assertTrue(p1 in value or p2 in value, "Incorrect policy type value")


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
