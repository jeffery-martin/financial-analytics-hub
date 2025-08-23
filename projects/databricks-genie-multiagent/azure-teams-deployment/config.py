#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """Bot Configuration"""

    PORT = 3978
    APP_ID = "YourAppId" # This is the application ID for the bot service.
    APP_PASSWORD = "YourAppPAssword"  # This is the password for the bot service.
    APP_TYPE = "SingleTenant" # "SingleTenant" or "MultiTenant"
    #APP_TYPE = "MultiTenant" You can use this if testing locally
    APP_TENANTID = "YourTenantID" # This is the tenant ID for the bot service.
    DATABRICKS_SPACE_ID="YourSpaceID"
    DATABRICKS_HOST="https://yourdatabricksworkspace.cloud.databricks.com"
    DATABRICKS_TOKEN="YourDatabricksToken"