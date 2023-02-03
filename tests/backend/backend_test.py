import unittest
import requests
import pandas as pd
import os

class CPDBBackendTest(unittest.TestCase):

  cpdb_path = "climate_policy_database_policies_export.csv"
  groundTruthColNames = {
      "country_iso": 'Country ISO',
      "sector": 'Sector name',
      "policy_instrument": 'Type of policy instrument',
      "policy_type": "Policy type",
      "implement_state": "Implementation state",
      "decision_date": "Date of decision"
  }

  groud_truth = pd.read_csv(cpdb_path)

  def readCPDB(self):
    return CPDBBackendTest.groud_truth

  def readAPI(self, params = dict()):
    API_URL = os.getenv("API_URL")
    user_name = os.getenv("API_USER")
    password = os.getenv("API_PASSWORD")
    response = requests.get(API_URL, auth=(user_name, password), params=params)
    return pd.read_json(response.content)

  def testNoFilter_returnsSameNumberOfRows(self):
    expected = self.readCPDB()
    actual = self.readAPI()
    self.assertEqual(actual.shape[0], expected.shape[0], "incorrect raw record number")

  def testCountryISOFilter_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["country_iso"]] == "IND"]
    actual = self.readAPI(dict(country_iso = ["IND"]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testPolicySingleSector_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    sectorName = "General"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["sector"]].str.contains(sectorName)]
    actual = self.readAPI(dict(sector = [sectorName]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testPolicyMultipleSectors_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    sectorNames = ["General", "Electricity and heat"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["sector"]].str.contains('|'.join(sectorNames)) == True]
    actual = self.readAPI(dict(sector = ",".join(sectorNames))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSinglePolicyInstrument_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policyInstrument = "Direct investment"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains(policyInstrument)]
    actual = self.readAPI(dict(policy_instrument = [policyInstrument]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultiplePolicyInstrument_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policyInstrument = ["Fiscal or financial incentives", "Institutional creation"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains('|'.join(policyInstrument)) == True]
    actual = self.readAPI(dict(policy_instrument = ",".join(policyInstrument))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSinglePolicyType_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policy_type = "Energy efficiency"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_type"]].str.contains(policy_type)]
    actual = self.readAPI(dict(policy_type = [policy_type]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultiplePolicyType_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policy_type = ["Energy efficiency", "Renewables"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_type"]].str.contains('|'.join(policy_type)) == True]
    actual = self.readAPI(dict(policy_type = ",".join(policy_type))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSingleImplementState_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    implement_state = "In force"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["implement_state"]].str.contains(implement_state)]
    actual = self.readAPI(dict(implement_state = [implement_state]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultipleImplementState_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    implement_state = ["In force", "Planned"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["implement_state"]].str.contains('|'.join(implement_state)) == True]
    actual = self.readAPI(dict(implement_state = ",".join(implement_state))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSingleDecisionDate_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    decision_date = 2010
    filteredGroundTruth = cpdb[(cpdb[CPDBBackendTest.groundTruthColNames["decision_date"]] == decision_date)]
    actual = self.readAPI(dict(decision_date = [decision_date]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultipleDecisionDate_equalToTheFirstValue(self):
    cpdb = self.readCPDB()
    decision_date = [2010, 2012]
    filteredGroundTruth_2010 = cpdb[(cpdb[CPDBBackendTest.groundTruthColNames["decision_date"]] == decision_date[0])]
    filteredGroundTruth_2012 = cpdb[(cpdb[CPDBBackendTest.groundTruthColNames["decision_date"]] == decision_date[1])]
    filteredGroundTruth = pd.concat([filteredGroundTruth_2010, filteredGroundTruth_2012]).drop_duplicates()
    actual = self.readAPI(dict(decision_date = ",".join([str(x) for x in decision_date])))
    self.assertEqual(actual.shape[0], filteredGroundTruth_2010.shape[0], "incorrect record number")

  def testMixedFilters_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    country_iso = "IND"
    sector_name = "General"
    policy_instrument = "Direct investment"
    policy_type = "Energy efficiency"
    implement_state = "In force"
    decision_date = 2010
    criteria = (cpdb[CPDBBackendTest.groundTruthColNames["country_iso"]] == country_iso) & \
               (cpdb[CPDBBackendTest.groundTruthColNames["sector"]].str.contains(sector_name)) & \
               (cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains(policy_instrument)) & \
               (cpdb[CPDBBackendTest.groundTruthColNames["policy_type"]].str.contains(policy_type)) & \
               (cpdb[CPDBBackendTest.groundTruthColNames["implement_state"]].str.contains(implement_state)) & \
               (cpdb[CPDBBackendTest.groundTruthColNames["decision_date"]] == decision_date)
    filteredGroundTruth = cpdb[criteria]
    actual = self.readAPI(dict(country_iso = country_iso, sector = sector_name, policy_instrument = policy_instrument, policy_type=policy_type, implement_state = implement_state, decision_date=decision_date))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")




if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)