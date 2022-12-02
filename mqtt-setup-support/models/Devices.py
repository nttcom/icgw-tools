## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

import io
import requests
from azure.iot.hub import IoTHubRegistryManager
from google.cloud import iot_v1
from google.cloud.iot_v1.types import resources
from google.protobuf import field_mask_pb2 as gp_field_mask
from google.oauth2 import service_account
from msrest.exceptions import HttpOperationError
from typing import List, Literal


class CloudSetting:
    def add(self):
        pass

    def get_info(self) -> str:
        pass


class AzureSetting(CloudSetting):
    def __init__(self, connection_string: str, device_id: str, options: dict = None):
        self.device_id = device_id
        self.options = options
        self.iothub_registry_manager = IoTHubRegistryManager(connection_string)

    def add(self):
        """
        Add or Update Azure Device to Azure IoT with Hub is the given connection string
        """
        # Get Basic info
        auth_type = self.__get_auth_type()
        status = self.__get_status()

        # Check if device is created or not
        device = self.__get_device()

        try:
            if device is None:
                return self.__create_device(auth_type=auth_type, status=status)
            else:
                return self.__update_device(
                    etag=device.etag, auth_type=auth_type, status=status
                )
        except HttpOperationError as ex:
            response: requests.Response = ex.response
            raise Exception(response.json())

    def get_info(self):
        """
        Get the information of the setting
        """
        return f"Cloud Service: Azure IoT, Device ID: {self.device_id}"

    def __create_device(
        self,
        auth_type: Literal["SAS", "CA", "X509"],
        status: Literal["enabled", "disabled"],
    ):
        """
        Create Azure Device
        """
        if auth_type == "SAS":
            return self.iothub_registry_manager.create_device_with_sas(
                device_id=self.device_id,
                primary_key=self.options["primary_key"],
                secondary_key=self.options["secondary_key"],
                status=status,
            )
        elif auth_type == "X509":
            return self.iothub_registry_manager.create_device_with_x509(
                device_id=self.device_id,
                primary_thumbprint=self.options["primary_thumbprint"],
                secondary_thumbprint=self.options["secondary_thumbprint"],
                status=status,
            )
        else:
            return (
                self.iothub_registry_manager.create_device_with_certificate_authority(
                    device_id=self.device_id, status=status
                )
            )

    def __update_device(
        self,
        etag: str,
        auth_type: Literal["SAS", "CA", "X509"],
        status: Literal["enabled", "disabled"],
    ):
        """
        Update Azure Device
        """
        if auth_type == "SAS":
            return self.iothub_registry_manager.update_device_with_sas(
                device_id=self.device_id,
                etag=etag,
                primary_key=self.options["primary_key"],
                secondary_key=self.options["secondary_key"],
                status=status,
            )
        elif auth_type == "X509":
            return self.iothub_registry_manager.update_device_with_x509(
                device_id=self.device_id,
                etag=etag,
                primary_thumbprint=self.options["primary_thumbprint"],
                secondary_thumbprint=self.options["secondary_thumbprint"],
                status=status,
            )
        else:
            return (
                self.iothub_registry_manager.update_device_with_certificate_authority(
                    device_id=self.device_id, etag=etag, status=status
                )
            )

    def __get_device(self):
        """
        Check and get device is created in cloud
        """
        try:
            return self.iothub_registry_manager.get_device(self.device_id)
        except Exception:
            return None

    def __get_auth_type(self):
        """
        Get Authentication Type, only SAS, CA or X509 will be accepted
        """
        if "type" in self.options:
            auth_type = str(self.options["type"]).upper()
            if auth_type == "SAS" or auth_type == "CA" or auth_type == "X509":
                return auth_type
            else:
                raise Exception("Invalid auth type {}".format(self.options["type"]))
        else:
            raise Exception("Invalid as empty auth type")

    def __get_status(self):
        """
        Get the status value from options
        """
        if "status" in self.options:
            status = str(self.options["status"]).lower()
            return status if status == "enabled" or status == "disabled" else "enabled"
        else:
            return "enabled"


class GcpSetting(CloudSetting):
    def __init__(
        self,
        project_id: str,
        region: str,
        registry_id: str,
        device_id: str,
        options: dict = None,
        sa_path: str = None,
    ):
        # If service account is provided, use that
        credentials: service_account.Credentials = None
        if sa_path is not None:
            credentials = service_account.Credentials.from_service_account_file(sa_path)

        self.client = iot_v1.DeviceManagerClient(credentials=credentials)
        self.project_id = project_id
        self.region = region
        self.registry_id = registry_id
        self.device_id = device_id
        self.options = options

    def add(self):
        """
        Add GCP Device to GCP IoT
        """

        # Check if device is created or not
        device = self.__get_device()

        try:
            if device is None:
                return self.__create_device()
            else:
                return self.__update_device(device=device)
        except Exception as ex:
            raise ex

    def get_info(self):
        """
        Get the information of the setting
        """
        return f"Cloud Service: GCP IoT, Device ID: {self.device_id}"

    def __create_device(self):
        """
        Create GCP Device
        """
        parent = self.client.registry_path(
            self.project_id, self.region, self.registry_id
        )
        device_template = {"id": self.device_id}

        # Get Key Format
        key_format = self.__get_key_format()

        # If Key Format is found, set the public key
        if key_format is not None:
            certificate = self.__load_public_key()
            device_template["credentials"] = [
                {
                    "public_key": {
                        "format": key_format,
                        "key": certificate,
                    }
                }
            ]

        return self.client.create_device(
            request={"parent": parent, "device": device_template}
        )

    def __update_device(self, device: resources.Device):
        """
        Update GCP Device
        """
        # Get Key Format
        key_format = self.__get_key_format()

        # Set Mask
        mask = gp_field_mask.FieldMask()
        mask.paths.append("credentials")

        # If Key Format is found, set the public key
        if key_format is not None:
            certificate = self.__load_public_key()
            key = iot_v1.PublicKeyCredential(format=key_format, key=certificate)
            cred = iot_v1.DeviceCredential(public_key=key)

            device.id = b""
            device.num_id = 0
            device.credentials = [cred]
        else:
            device.id = b""
            device.num_id = 0
            device.credentials = None

        return self.client.update_device(
            request={"device": device, "update_mask": mask}
        )

    def __get_device(self):
        """
        Check and get device is created in cloud
        """
        try:
            device_path = self.client.device_path(
                self.project_id, self.region, self.registry_id, self.device_id
            )
            return self.client.get_device(request={"name": device_path})
        except Exception:
            return None

    def __get_key_format(self):
        """
        Get Public Key Format
        """
        if "format" in self.options:
            f = str(self.options["format"]).upper().strip()
            if f == "RSA_PEM":
                return iot_v1.PublicKeyFormat.RSA_PEM
            elif f == "RSA_X509_PEM":
                return iot_v1.PublicKeyFormat.RSA_X509_PEM
            elif f == "ES256_PEM":
                return iot_v1.PublicKeyFormat.ES256_PEM
            elif f == "ES256_X509_PEM":
                return iot_v1.PublicKeyFormat.ES256_X509_PEM
            elif f == "":
                return None
            else:
                raise Exception(
                    "Invalid Public Key Format {}".format(self.options["format"])
                )
        else:
            return None

    def __load_public_key(self):
        """
        Load public key from specific path
        """
        certificate = None
        with io.open(self.options["public_key"]) as f:
            certificate = f.read()
        if certificate is None:
            raise Exception(
                "Unable to load public key {}".format(self.options["public_key"])
            )
        return certificate
