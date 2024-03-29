"""A Python API for NewClimate Institute's ClimatePolicy DataBase (CPDB)."""

import json

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

API_URL = 'https://climatepolicydatabase.org/api/v1/climate-policies'


class Request:
    """
    A Request formatted to issue to the ClimatePolicy Database. Unless manually inserted with
    Request.set_request_json, all requests generated by this API are guaranteed to adhere to the request_schema.json
    """

    def __init__(self, api_url=API_URL):
        self._api_url = api_url
        self._request = ""
        self._api_user = ""
        self._api_password = ""
        self._country = ""
        self._decision_date = ""
        self._policy_status = ""
        self._response = ""
        self._sector = ""
        self._policy_instrument = ""
        self._mitigation_area = ""
        self._data_frame = ""
        self._properties = dict()

    def set_country(self, c):
        """
        :param c: the name of the ISO country code
        :return: none
        """
        # sets a string country for this request
        self._country = c

    def set_decision_date(self, d):
        """
        Sets the decision date to provided year.
        :param d: the decision date in YYYY format as an integer
        :return: none
        """
        self._decision_date = d

    def set_policy_status(self, s):
        """
        Sets the policy status (implemention state) for the request. Should be one of
        (case-insensitive):
        { Draft, Ended, In force, Planned, Superseded, Under review, Unknown }

        :param s:
        :return: none
        """
        self._policy_status = s.lower()

    def add_sector(self, sector):
        """
        Adds sectors to query (Case insensitive). Each provided sector must be one of the sectors from the section of
        the same name on https://climatepolicydatabase.org/policies.
        Some examples: agriculture and forestry or CCS.

        :param sector: a list of sectors to add to the query.
        :return: none
        """
        if self._sector == "":
          self._sector = sector
        else:
          self._sector = ",".join([self._sector, sector])

    def add_policy_instrument(self, policy_instrument):
        """
        Adds policy instruments to the list of policy instruments to query for. Case insensitive. Each provided policy
        instrument must be from the section of the same name on https://climatepolicydatabase.org/policies.
        Some examples: grid access and priority for renewables or
        strategic planning. Note that for policy instruments that are grouped on the website,
        e.g. performance label, the server will treat it as a query for all contained groups.

        :param policy_instrument: a list of policy instruments to add to the query.
        :return: none
        """
        if self._policy_instrument == "":
          self._policy_instrument = policy_instrument
        else:
          self._policy_instrument = ",".join([self._policy_instrument, policy_instrument])

    def add_mitigation_area(self, mitigation_area):
        """
        A list of mitigation areas to query. Items must be one of:
        energy efficiency, energy service demand reduction and resource efficiency, 
        non energy use, other low carbon technologies and fuel switch, renewables, unknown

        :param mitigation_area: a list of policy types to add to the query.
        :return: none
        """
        if self._mitigation_area == "":
          self._mitigation_area = mitigation_area
        else:
          self._mitigation_area = ",".join([self._mitigation_area, mitigation_area])

    # For request issuing & data retrieval.
    def issue(self):
        """
        Issues this request against the API.
        :return: the response from the server
        """
        req = self.marshal()
        resp = requests.get(self._api_url, auth=HTTPBasicAuth(self._api_user, self._api_password), params = req)
        resp.raise_for_status()  # raise any produced error
        self._response = resp.json()
        self._data_frame = pd.DataFrame.from_dict(self._response)
        return self._data_frame

    # For saving data in different formats
    def save_json(self, path):
        """
        :param path: the file to save the data to. The file type will be dependent on the value of
        self._response type
        :return: none
        """
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(self._response, f)

    def save_csv(self, path):
        """ 
        :param path: the file to save the data to. The file type will be dependent on the value of
        self._response_type
        :return: none
        """
        if self._data_frame is None:
          print("No dataframe set, unable to export to CSV")
          return
        self._data_frame.to_csv(path)

    # Helpers for issuing the request
    def marshal(self):
        """
        Marshals this request into a JSON query for the API. This does not perform validation and may produce
        well-formed JSON that is not a valid request for the API.
        :return: a JSON request containing the values of this Request.
        """
        if self._request != "":
            return
        properties = dict()
        if self._country != "":
            properties["country_iso"] = self._country
        if self._decision_date != "":
            properties["decision_date"] = self._decision_date
        if self._policy_status != "":
            properties["policy_status"] = self._policy_status
        if self._sector != "":
            properties["sector"] = self._sector
        if self._policy_instrument != "":
            properties["policy_instrument"] = self._policy_instrument
        if self._mitigation_area != "":
            properties["policy_type"] = self._mitigation_area
        self._properties = properties
        return properties

    # Helpers for testing
    def set_request(self, r):
        """
        :param r: the request, in proper JSON format (for testing)
        :return: none
        """
        self._request = r

    def set_api_user(self, u):
        """
        Sets the API username for the request.
        :param u: the username to be used for authenticating to the API
        :return: none
        """
        self._api_user = u

    def set_api_password(self, p):
        """
        Sets the API password for the request.
        :param p: the password to be used for authenticating to the API
        :return: none
        """
        self._api_password = p

