## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

from argparse import ArgumentParser
from services.main_service import MainService


__version__ = "1.0.0"


if __name__ == "__main__":

    try:
        parser = ArgumentParser(description="MQTTv2 transfer tool")
        parser.add_argument(
            "action",
            help="Current valid actions: 'update-sims', 'add-devices', 'add-authentications'",
            type=str,
        )
        parser.add_argument(
            "files",
            help="The file path of the data file, you can specify multiple files by using space between files",
            nargs="+",
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=__version__,
            help="Show version and exit",
        )
        args = parser.parse_args()

        if (
            args.action != "update-sims"
            and args.action != "add-devices"
            and args.action != "add-authentications"
        ):
            exit(
                "Invalid action, current valid actions: 'update-sims', 'add-devices', 'add-authentications'"
            )

        main = MainService()

        if args.action == "update-sims":
            main.batch_update_sims(*args.files)

        if args.action == "add-devices":
            main.add_devices(*args.files)

        if args.action == "add-authentications":
            main.add_authentications(*args.files)

    except Exception as ex:
        exit(str(ex))
