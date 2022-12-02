## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

import json
from models.SIM import UpdateSIMRequest
from models.Authentications import (
    CreateAzureAuthenticationRequest,
    CreateGCPAuthenticationRequest,
)
import requests
import urllib3
from typing import Union, Optional


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SDP:
    def __init__(self, endpoint: str, version: str = "v1") -> None:
        """
        Constructor of ICGW API Service
        """
        self._endpoint: str = endpoint
        self._version: str = version
        self._auth: bool = False
        self._tenant_id: str = None
        self._auth_token: str = None

    # Generate Token

    def generate_token(self, name: str, password: str, tenant_id: str):
        """
        Generate a token from the Keystone
        """
        payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "domain": {"id": "default"},
                            "name": name,
                            "password": password,
                        }
                    },
                },
                "scope": {"project": {"id": tenant_id}},
            }
        }
        url = "https://api.ntt.com/keystone/v3/auth/tokens?nocatalog"

        headers, _ = self.__execute_api(
            url, payload=json.dumps(payload), with_auth_token=False
        )

        if "X-Subject-Token" in headers:
            self._auth = True
            self._auth_token = headers["X-Subject-Token"]
            self._tenant_id = tenant_id
        else:
            raise Exception("No auth token is returned")

    # Group

    def get_groups(self):
        """
        Get Groups
        """
        url = f"groups"
        _, res = self.__execute_api(url, method="GET")
        return res

    # SIM

    def get_sims(self):
        """
        Get Sims
        """
        url = f"sims"
        _, res = self.__execute_api(url, method="GET")
        return res

    def get_sim(self, imsi: str):
        """
        Get Sim
        """
        url = f"sims/{imsi}"
        _, res = self.__execute_api(url, method="GET")
        return res

    def update_sim(self, imsi: str, req: UpdateSIMRequest):
        """
        Update SIM
        """
        url = f"sims/{imsi}"
        _, res = self.__execute_api(url, method="PUT", payload=req.toJSON())
        return res

    def get_authentications(
        self, type: str = "", name: str = "", page: int = 1, pageSize: int = 20
    ):
        """
        Get Authentications
        """
        url = f"authentications"
        params: Dict = {}
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        params["page"] = page
        params["pageSize"] = pageSize
        _, res = self.__execute_api(url, method="GET", params=params)
        return res

    def get_authentication(self, type: str, name: str):
        """
        Get Only The First Matching Authentication with type and name
        """
        auths = self.get_authentications()
        page, totalPages = auths["page"], auths["totalPages"]

        res: Optional[Dict] = None
        while page <= totalPages:
            r = self.get_authentications(type=type, name=name, page=page)
            if len(r["authentications"]) >= 1:
                res = r["authentications"][0]
                break
            page += 1
        return res

    def create_authentication(
        self,
        req: Union[CreateAzureAuthenticationRequest, CreateGCPAuthenticationRequest],
    ):
        """
        Create Authentication
        """
        url = f"authentications"
        _, res = self.__execute_api(url, method="POST", payload=req.toJSON())
        return res

    # PRIVATE

    def __execute_api(
        self,
        api_url: str,
        method: str = "POST",
        payload=None,
        params=None,
        with_auth_token=True,
    ) -> requests.Response:
        """
        Send HTTP requests to SDP API
        """
        if "http://" in api_url or "https://" in api_url:
            url = api_url
        else:
            url = "https://{}/{}/tenants/{}/{}".format(
                self._endpoint, self._version, self._tenant_id, api_url
            )

        headers = {}
        headers["Accept"] = "application/json"

        if with_auth_token and self._auth_token is not None:
            headers["X-Auth-Token"] = self._auth_token

        if payload is not None:
            headers["Content-Type"] = "application/json"

        resp: requests.Response = requests.request(
            method, url, headers=headers, data=payload, verify=False, params=params
        )
        if resp.status_code >= 400:
            raise Exception(resp.text)

        response_text = (
            json.loads(resp.text) if resp.text is not None and resp.text != "" else None
        )

        return resp.headers, response_text
