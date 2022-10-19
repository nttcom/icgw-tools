## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-mqtt-support-tool/blob/main/LICENSE

import allure
import pytest

from services.main_service import MainService
from tests.base import TestBase
from unittest.mock import Mock


class TestMainService(TestBase):
    @pytest.fixture(autouse=True)
    def _setup(self):
        """
        Common setup
        """

        # Mock Service
        self.mock_service = None

    @pytest.mark.parametrize(
        "content, value",
        [
            ({"azureSettings": Mock()}, "azure"),
            ({"gcpSettings": Mock()}, "gcp"),
            ({"abc": Mock()}, None),
        ],
    )
    def test_get_yaml_file_type(self, mocker, content, value):
        self.__mock_init(mocker)

        if value is not None:
            res = self.mock_service._MainService__get_yaml_file_type(content)
            assert str(res) == value
        else:
            with pytest.raises(Exception) as error_response:
                self.mock_service._MainService__get_yaml_file_type(content)
            assert str(error_response.value) == "Invalid yaml format"

    # Common

    def __mock_init(self, mocker):
        """
        Initialization of CacheService with mocks
        """
        # mock constructor
        self.mock_service = MainService()
