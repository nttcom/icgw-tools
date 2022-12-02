## Copyright (c) 2022 NTT Communications Corporation
##
## This software is released under the MIT License.
## see https://github.com/nttcom/icgw-tools/blob/main/LICENSE

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


SDP_API_HOST = os.environ.get("SDP_API_HOST")
SDP_API_TENANT_ID = os.environ.get("SDP_API_TENANT_ID")

SDP_API_KEY = os.environ.get("SDP_API_KEY")
SDP_API_SECRET = os.environ.get("SDP_API_SECRET")

if not SDP_API_HOST:
    raise Exception(f"Required Environment variable [SDP_API_HOST] does not exist")

if not SDP_API_TENANT_ID:
    raise Exception(f"Required Environment variable [SDP_API_TENANT_ID] does not exist")

if not SDP_API_KEY:
    raise Exception(f"Required Environment variable [SDP_API_KEY] does not exist")

if not SDP_API_SECRET:
    raise Exception(f"Required Environment variable [SDP_API_SECRET] does not exist")
