## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

import json
from typing import List


class UpdateSIMRecord:
    def __init__(
        self, imsi: str, azure_device_id: str = None, gcp_device_id: str = None
    ):
        self.imsi = imsi
        self.azure_device_id = azure_device_id
        self.gcp_device_id = gcp_device_id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class SIM:
    def __init__(
        self,
        imsi: str = None,
        imei: str = None,
        msisdn: str = None,
        deviceName: str = None,
        ipAddresses: List[str] = [],
        groupId: str = None,
        systemId: str = None,
        mqttClientId: str = None,
        azureDeviceId: str = None,
        gcpDeviceId: str = None,
        hsn: str = None,
        optionData1: str = None,
        optionData2: str = None,
        optionData3: str = None,
        activation: bool = True,
    ):
        self.imsi = imsi
        self.imei = imei
        self.msisdn = msisdn
        self.deviceName = deviceName
        self.ipAddresses = ipAddresses
        self.groupId = groupId
        self.systemId = systemId
        self.mqttClientId = mqttClientId
        self.azureDeviceId = azureDeviceId
        self.gcpDeviceId = gcpDeviceId
        self.hsn = hsn
        self.optionData1 = optionData1
        self.optionData2 = optionData2
        self.optionData3 = optionData3
        self.activation = activation

    def to_update_request(self):
        return UpdateSIMRequest(
            imei=self.imei,
            msisdn=self.msisdn,
            deviceName=self.deviceName,
            groupId=self.groupId,
            systemId=self.systemId,
            mqttClientId=self.mqttClientId,
            azureDeviceId=self.azureDeviceId,
            gcpDeviceId=self.gcpDeviceId,
            optionData1=self.optionData1,
            optionData2=self.optionData2,
            optionData3=self.optionData3,
        )

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class UpdateSIMRequest:
    def __init__(
        self,
        imei: str = None,
        msisdn: str = None,
        deviceName: str = None,
        groupId: str = None,
        systemId: str = None,
        mqttClientId: str = None,
        azureDeviceId: str = None,
        gcpDeviceId: str = None,
        optionData1: str = None,
        optionData2: str = None,
        optionData3: str = None,
    ):
        self.imei = imei
        self.msisdn = msisdn
        self.deviceName = deviceName
        self.groupId = groupId
        self.systemId = systemId
        self.mqttClientId = mqttClientId
        self.azureDeviceId = azureDeviceId
        self.gcpDeviceId = gcpDeviceId
        self.optionData1 = optionData1
        self.optionData2 = optionData2
        self.optionData3 = optionData3

    def toJSON(self):
        original = json.loads(json.dumps(self, default=lambda o: o.__dict__))
        return json.dumps({k: v for k, v in original.items() if v is not None})
