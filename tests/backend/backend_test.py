import unittest
import requests
import pandas as pd

class CPDBBackendTest(unittest.TestCase):

  cpdb_path = "climate_policy_database_policies_export.csv"
  groundTruthColNames = {
      "country_iso": 'Country ISO',
      "sector": 'Sector name',
      "policy_instrument": 'Type of policy instrument',
      "mitigation_area": "Policy type",
      "status": "Implementation state",
      "decision_date": "Date of decision"
  }

  groud_truth = pd.read_csv(cpdb_path)

  def readCPDB(self):
    return CPDBBackendTest.groud_truth

  def readAPI(self, params = dict()):
    API_URL = 'http://cpdb-dev.waat.eu/api/v1/climate-policies'
    user_name = 'user'
    password = 'WaatUser'
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
    actual = self.readAPI(dict(sectors = [sectorName]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testPolicyMultipleSectors_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    sectorNames = ["General", "Electricity and heat"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["sector"]].str.contains('|'.join(sectorNames)) == True]
    actual = self.readAPI(dict(sectors = ",".join(sectorNames))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSinglePolicyInstrument_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policyInstrument = "Direct investment"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains(policyInstrument)]
    actual = self.readAPI(dict(policy_instruments = [policyInstrument]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultiplePolicyInstrument_returnSameNumberOfRows(self):
    cpdb = self.readCPDB()
    policyInstrument = ["Fiscal or financial incentives", "Institutional creation"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains('|'.join(policyInstrument)) == True]
    actual = self.readAPI(dict(policy_instruments = ",".join(policyInstrument))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSingleMitigationArea_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    mitigation_area = "Energy efficiency"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["mitigation_area"]].str.contains(mitigation_area)]
    actual = self.readAPI(dict(mitigation_areas = [mitigation_area]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultipleMitigationArea_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    mitigation_area = ["Energy efficiency", "Renewables"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["mitigation_area"]].str.contains('|'.join(mitigation_area)) == True]
    actual = self.readAPI(dict(mitigation_areas = ",".join(mitigation_area))).drop_duplicates()
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testSingleStatus_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    status = "In force"
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["status"]].str.contains(status)]
    actual = self.readAPI(dict(status = [status]))
    self.assertEqual(actual.shape[0], filteredGroundTruth.shape[0], "incorrect record number")

  def testMultipleStatus_returnsSameNumberOfRows(self):
    cpdb = self.readCPDB()
    status = ["In force", "Planned"]
    filteredGroundTruth = cpdb[cpdb[CPDBBackendTest.groundTruthColNames["status"]].str.contains('|'.join(status)) == True]
    actual = self.readAPI(dict(status = ",".join(status))).drop_duplicates()
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
    pass
    # cpdb = self.readCPDB()
    # country_iso = "IND"
    # sectorName = "General"
    # policyInstrument = "Direct investment"
    # mitigation_area = "Energy efficiency"
    # status = "In force"
    # decision_date = 2010
    # criteria = (cpdb[CPDBBackendTest.groundTruthColNames["country_iso"]] == country_iso) & \
    #            (cpdb[cpdb[CPDBBackendTest.groundTruthColNames["sector"]].str.contains(sectorName)]) & \
    #            (cpdb[cpdb[CPDBBackendTest.groundTruthColNames["policy_instrument"]].str.contains(policyInstrument)]) & \
    #            (cpdb[cpdb[CPDBBackendTest.groundTruthColNames["mitigation_area"]].str.contains(mitigation_area)]) & \
    #            (cpdb[CPDBBackendTest.groundTruthColNames["status"]].str.contains(status)) & \
    #            (cpdb[CPDBBackendTest.groundTruthColNames["decision_date"]] == decision_date)
    # filteredGroundTruth = cpdb[criteria]
    # actual = self.readAPI(dict(country_iso = country_iso, sector = sectorName, policyInstrument))




if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)