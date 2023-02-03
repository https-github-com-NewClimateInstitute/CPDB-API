"""A Python API for NewClimate Institute's ClimatePolicy DataBase (CPDB).
"""

import json
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

API_URL = 'http://cpdb-dev.waat.eu/api/v1/climate-policies'

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
        self._status = ""
        self._response = ""
        self._sectors = ""
        self._policy_instruments = ""
        self._mitigation_areas = ""
        self._data_frame = ""
        self._properties = dict()

    # Pre-formatted requests
    def set_request(self, r):
        """
        :param r: the request, in proper JSON format per https://github/<path>/<to>/<version>/<controlled>/<schema>
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

    def set_status(self, s):
        """
        Sets the status of the request. Should be one of (case-insensitive):
        { Draft, Ended, In force, Planned, Superseded, Under review, Unknown }

        :param s:
        :return:
        """
        self._status = s.lower()

    def add_sectors(self, sectors):
        """
        Adds sectors to query (Case insensitive). Each provided sector must be one of the sectors from the section of
        the same name on https://climatepolicydatabase.org/policies.
        Some examples: agriculture and forestry or CCS.

        :param sectors: a list of sectors to add to the query.
        :return: none
        """
        self._sectors = ",".join(sectors)

    def add_policy_instruments(self, policy_instruments):
        """
        Adds policy instruments to the list of policy instruments to query for. Case insensitive. Each provided policy
        instrument must be from the section of the same name on https://climatepolicydatabase.org/policies.
        Some examples: grid access and priority for renewables or
        strategic planning. Note that for policy instruments that are grouped on the website,
        e.g. performance label, the server will treat it as a query for all contained groups.

        :param policy_instruments: a list of policy instruments to add to the query.
        :return: none
        """
        self._policy_instruments = ",".join(policy_instruments)

    def add_mitigation_areas(self, mitigation_areas):
        """
        A list of mitigation areas to query. Items must be one of:energy efficiency,
        energy service demand reduction and resource efficiency, non energy use,
        other low carbon technologies and fuel switch, renewables, unknown

        :param mitigation_areas: a list of mitigation areas to add to the query.
        :return: none
        """
        self._mitigation_areas = ",".join(mitigation_areas)

    # For request issuing & data retrieval.
    def issue(self):
        """
        Issues this request against the API.
        :return: the response from the server
        """
        req = self.marshal()
        resp = requests.get(self._api_url, auth=HTTPBasicAuth(self._api_user, self._api_password), params = req, timeout=300)
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
        if self._status != "":
            properties["status"] = self._status
        if self._sectors != "":
            properties["sectors"] = self._sectors
        if self._policy_instruments != "":
            properties["policy_instruments"] = self._policy_instruments
        if self._mitigation_areas != "":
            properties["mitigation_areas"] = self._mitigation_areas
        self._properties = properties
        return properties