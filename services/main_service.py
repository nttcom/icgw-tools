## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-mqtt-support-tool/blob/main/LICENSE

from typing import Dict, List
from libs.SDP import SDP
from models.Devices import AzureSetting, CloudSetting, GcpSetting
from models.SIM import SIM, UpdateSIMRecord
from models.Authentications import AzureAuthentication, GCPAuthentication
from settings import SDP_API_HOST, SDP_API_KEY, SDP_API_SECRET, SDP_API_TENANT_ID
import logging
import yaml

stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
log = logging.getLogger("pythonConfig")
log.setLevel(logging.INFO)
log.addHandler(stream)


class MainService:
    def __init__(self) -> None:
        self.sdp = SDP(endpoint=SDP_API_HOST)

    def batch_update_sims(self, *args):
        """
        Batch update SIMs with adding `azureDeviceId` and `gcpDeviceId` to current SIM records.
        """

        # Generate Token as SDP API is needed
        self.sdp.generate_token(
            name=SDP_API_KEY, password=SDP_API_SECRET, tenant_id=SDP_API_TENANT_ID
        )

        # Load data from given yaml files
        data = self.__load_batch_update_sims_from_files(*args)

        # Loop all IMSI
        for imsi, update_record in data.items():

            try:
                # Get the SIM object from API
                sim = SIM(**self.sdp.get_sim(imsi=imsi))

                # Set azure if it is set in yaml
                if update_record.azure_device_id is not None:
                    sim.azureDeviceId = update_record.azure_device_id

                # Set gcp if it is set in yaml
                if update_record.gcp_device_id is not None:
                    sim.gcpDeviceId = update_record.gcp_device_id

                # Update SIM by API
                res = self.sdp.update_sim(imsi=imsi, req=sim.to_update_request())

                log.info(f"[\033[92m SUCCESS \033[0m] IMSI [{imsi}].")
            except Exception as e:
                log.error(f"[\033[91m FAILED \033[0m] IMSI [{imsi}]. Response: {e}")

    def add_authentications(self, *args):
        """
        Add authentications for Azure IoT and GCP IoT services.
        """

        # Generate Token as SDP API is needed
        self.sdp.generate_token(
            name=SDP_API_KEY, password=SDP_API_SECRET, tenant_id=SDP_API_TENANT_ID
        )

        # Load data from given yaml files
        auths = self.__load_batch_create_authentications_from_files(*args)

        # Loop all Authentications
        for auth in auths:
            try:
                res = self.sdp.create_authentication(req=auth.to_create_request())
                log.info(
                    f"[\033[92m SUCCESS \033[0m] Add Authentication [{res['name']}]."
                )
            except Exception as e:
                log.error(
                    f"[\033[91m FAILED \033[0m] Add Authentication [{res['name']}]. Response: {e}"
                )

    def add_devices(self, *args):
        """
        Add devices to Azure IoT and GCP IoT services.
        """

        try:
            settings = self.__load_add_devices_from_files(*args)

            for s in settings:
                try:
                    res = s.add()
                    log.info(f"[\033[92m SUCCESS \033[0m] Add Device [{s.get_info()}].")
                except Exception as e:
                    log.error(
                        f"[\033[91m FAILED \033[0m] Add Device [{s.get_info()}]. Response: {e}"
                    )
        except Exception as e:
            log.error(f"[\033[91m FAILED \033[0m] Fatal Error: {e}")

    # PRIVATE FUNCTIONS

    def __load_batch_update_sims_from_files(self, *args):
        """
        Load update records from given yaml files
        """
        data: Dict[str, UpdateSIMRecord] = {}

        for filename in args:
            (device_type, res) = self.__load_device_id_from_yaml(filename=filename)

            for imsi, device_id in res.items():
                if not imsi in data.keys():
                    rec = UpdateSIMRecord(imsi=imsi)
                    data[imsi] = rec

                if device_type == "azure":
                    data[imsi].azure_device_id = device_id
                elif device_type == "gcp":
                    data[imsi].gcp_device_id = device_id

        return data

    def __load_device_id_from_yaml(self, filename):
        """
        Load a given yaml file and return the imsi-deviceName dictionary
        """
        res = {}
        with open(filename, "r") as yml:
            yml_content = yaml.safe_load(yml)

        device_type: str = self.__get_yaml_file_type(yml_content)

        devices = yml_content[device_type + "Settings"]["devices"]

        for device in devices:
            res[device["imsi"]] = device["deviceId"]

        return device_type, res

    def __load_batch_create_authentications_from_files(self, *args):
        """
        Load create records from given yaml files
        """
        data: List = []

        for filename in args:
            (device_type, res) = self.__load_authentications_from_yaml(
                filename=filename
            )

            for auth in res:
                if device_type == "azure":
                    data.append(AzureAuthentication(**auth))
                elif device_type == "gcp":
                    data.append(GCPAuthentication(**auth))

        return data

    def __load_authentications_from_yaml(self, filename):
        """
        Load a given yaml file and return the authentications list
        """
        res: List = []
        with open(filename, "r") as yml:
            yml_content = yaml.safe_load(yml)

        device_type: str = self.__get_yaml_file_type(yml_content)

        auths = yml_content[device_type + "Settings"]["authentications"]

        for auth in auths:
            if device_type == "azure":
                ...
            elif device_type == "gcp":
                auth.update(self.__load_gcp_common_settings(yml_content))
            else:
                raise Exception(f"Unknown device type {device_type}")
            res.append(auth)

        return device_type, res

    def __load_add_devices_from_files(self, *args) -> List[CloudSetting]:
        """
        Load update records from given yaml files
        """
        settings: List[CloudSetting] = []

        for filename in args:

            log.info(f"Loading file {filename}...")

            with open(filename, "r") as yml:
                yml_content = yaml.safe_load(yml)

            device_type: str = self.__get_yaml_file_type(yml_content)

            if device_type == "azure":
                settings += self.__load_azure_detail(yml_content)
            elif device_type == "gcp":
                settings += self.__load_gcp_detail(yml_content)
            else:
                raise Exception(f"Unknown device type {device_type}")

        log.info(f"All files loaded. There are {len(settings)} devices will be added.")

        return settings

    def __get_yaml_file_type(self, content):
        """
        Check and get the cloud type of the yaml file
        """
        if "azureSettings" in content:
            return "azure"
        elif "gcpSettings" in content:
            return "gcp"
        else:
            raise Exception("Invalid yaml format")

    def __get_device_options(
        self, global_options: List[dict], device_options: List[dict] = None
    ):
        """
        Merge global options and device options and return the string of all options
        """

        option_dict = {}

        if global_options is not None:
            for option in global_options:
                option_dict[option["name"]] = option["value"]

        if device_options is not None:
            for option in device_options:
                option_dict[option["name"]] = option["value"]

        return option_dict

    def __load_azure_detail(self, yml_content):
        """
        Load Azure Setting from yaml content
        """
        settings: List[CloudSetting] = []

        connection_string: str = yml_content["azureSettings"]["connectionString"]
        options: List[dict] = (
            yml_content["azureSettings"]["options"]
            if "options" in yml_content["azureSettings"]
            else []
        )

        for device in yml_content["azureSettings"]["devices"]:
            device_options: List[dict] = (
                device["options"] if "options" in device else None
            )
            settings.append(
                AzureSetting(
                    connection_string=connection_string,
                    device_id=device["deviceId"],
                    options=self.__get_device_options(options, device_options),
                )
            )

        return settings

    def __load_gcp_detail(self, yml_content):
        """
        Load GCP Setting from yaml content
        """
        settings: List[CloudSetting] = []

        project_id = yml_content["gcpSettings"]["projectId"]
        region = yml_content["gcpSettings"]["region"]
        registry_id = yml_content["gcpSettings"]["registryId"]
        options: List[dict] = (
            yml_content["gcpSettings"]["options"]
            if "options" in yml_content["gcpSettings"]
            else []
        )
        service_account = (
            yml_content["gcpSettings"]["serviceAccount"]
            if "serviceAccount" in yml_content["gcpSettings"]
            else None
        )

        for device in yml_content["gcpSettings"]["devices"]:
            device_options: List[dict] = (
                device["options"] if "options" in device else None
            )
            settings.append(
                GcpSetting(
                    project_id=project_id,
                    region=region,
                    registry_id=registry_id,
                    device_id=device["deviceId"],
                    options=self.__get_device_options(options, device_options),
                    sa_path=service_account,
                )
            )

        return settings

    def __load_gcp_common_settings(self, yml_content):
        """
        Load GCP Project Detail from yaml content
        """
        settings: Dict = {}

        settings["projectId"] = yml_content["gcpSettings"]["projectId"]
        settings["region"] = yml_content["gcpSettings"]["region"]
        settings["registryId"] = yml_content["gcpSettings"]["registryId"]

        return settings
