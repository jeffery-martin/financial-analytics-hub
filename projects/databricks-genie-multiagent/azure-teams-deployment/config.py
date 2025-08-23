#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """Bot Configuration"""

    PORT = 3978
    APP_ID = "6db74ee0-d9eb-437f-84e6-067b873cf115" # This is the application ID for the bot service.
    APP_PASSWORD = "4_K8Q~~x4XiHAEe6o6jOoNSMSBQYsr1Kuco1UcUh"  # This is the password for the bot service.
    APP_TYPE = "SingleTenant" # "SingleTenant" or "MultiTenant"
    #APP_TYPE = "MultiTenant" You can use this if testing locally
    APP_TENANTID = "da77ffb1-ac97-492b-9f99-aec375868c10" # This is the tenant ID for the bot service.
    DATABRICKS_SPACE_ID="01f052b47d04167a84e7e866d4316efc"
    DATABRICKS_HOST="mdt-diabetes-dip-analytics-prod.cloud.databricks.com"
    DATABRICKS_TOKEN="dapi4ba8d9f34cf4850819c20bbcbe4bc530"
