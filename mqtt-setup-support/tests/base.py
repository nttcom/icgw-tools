## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE


class TestBase:

    # Private methods

    def _mock_method(
        self,
        mocker,
        original_class: str,
        original_method_name: str,
        target_method_name: str = None,
    ):
        """
        Mock service method with specific method
        """
        if target_method_name is None:
            target_method_name = original_method_name

        mock_method = getattr(self.mock_service, target_method_name)
        mocker.patch(
            "{}.{}".format(original_class, original_method_name),
            mock_method,
        )
