## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

import json
from typing import List
import io
from datetime import datetime


class CreateAzureAuthenticationRequest:
    def __init__(
        self,
        type: str = "",
        name: str = "",
        sharedAccessKey: str = "",
        description: str = "",
        deviceId: str = "",
    ):
        self.type = type
        self.name = name
        self.description = description
        self.sharedAccessKey = sharedAccessKey
        self.deviceId = deviceId

    def toJSON(self) -> str:
        original = json.loads(json.dumps(self, default=lambda o: o.__dict__))
        return json.dumps({k: v for k, v in original.items()})


class CreateGCPAuthenticationRequest:
    def __init__(
        self,
        type: str = "",
        name: str = "",
        description: str = "",
        projectId: str = "",
        region: str = "",
        registryId: str = "",
        deviceId: str = "",
        algorithm: str = "",
        privateKey: str = "",
    ):
        self.type = type
        self.name = name
        self.description = description
        self.projectId = projectId
        self.region = region
        self.registryId = registryId
        self.deviceId = deviceId
        self.algorithm = algorithm
        self.privateKey = privateKey

    def toJSON(self) -> str:
        original = json.loads(json.dumps(self, default=lambda o: o.__dict__))
        return json.dumps({k: v for k, v in original.items()})


class GCPAuthentication:
    def __init__(
        self,
        name: str = "",
        description: str = "",
        projectId: str = "",
        region: str = "",
        registryId: str = "",
        deviceId: str = "",
        algorithm: str = "",
        privateKey: str = "",
    ):
        self.__type = "gcp-iot-credentials"
        self.name = name
        self.description = description
        self.projectId = projectId
        self.region = region
        self.registryId = registryId
        self.deviceId = deviceId
        self.algorithm = algorithm
        self.privateKey = privateKey

    def to_create_request(self) -> CreateGCPAuthenticationRequest:
        return CreateGCPAuthenticationRequest(
            type=self.__type,
            name=self.__add_time_suffix(self.name),
            description=self.description,
            projectId=self.projectId,
            region=self.region,
            registryId=self.registryId,
            deviceId=self.deviceId,
            algorithm=self.algorithm,
            privateKey=self.__load_private_key(),
        )

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __add_time_suffix(self, value: str) -> str:
        suffix = datetime.now().strftime("%Y%m%d%H%M")
        return f"{value}_{suffix}"

    def __load_private_key(self) -> str:
        """
        Load private key from specific path
        """
        certificate = None
        with io.open(self.privateKey) as f:
            certificate = f.read()
        if certificate is None:
            raise Exception("Unable to load private key {}".format(self.privateKey))
        return certificate


class AzureAuthentication:
    def __init__(
        self,
        name: str = "",
        sharedAccessKey: str = "",
        description: str = "",
        deviceId: str = "",
    ):
        self.__type = "azure-iot-credentials"
        self.name = name
        self.description = description
        self.sharedAccessKey = sharedAccessKey
        self.deviceId = deviceId

    def to_create_request(self) -> CreateAzureAuthenticationRequest:
        return CreateAzureAuthenticationRequest(
            type=self.__type,
            name=self.__add_time_suffix(self.name),
            description=self.description,
            sharedAccessKey=self.sharedAccessKey,
            deviceId=self.deviceId,
        )

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __add_time_suffix(self, value: str) -> str:
        suffix = datetime.now().strftime("%Y%m%d%H%M")
        return f"{value}_{suffix}"
