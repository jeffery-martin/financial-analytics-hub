"""
Databricks Genie Bot

Authors: Luiz Carrossoni Neto, Ryan Bates
Revision: 1.1

This script implements an experimental chatbot that interacts with Databricks' Genie API. The bot facilitates conversations with Genie,
Databricks' AI assistant, through a chat interface.

Note: This is experimental code and is not intended for production use.


Update on May 02 to reflect Databricks API Changes https://www.databricks.com/blog/genie-conversation-apis-public-preview
Update on Aug 5 to reflect Microsoft Azure no longer supporting MultiTenant bots
"""

"""
Startup Command:
python3 -m aiohttp.web -H 0.0.0.0 -P 8000 app:init_func

"""

from asyncio.log import logger
import os
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from aiohttp import web
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI
import asyncio
import sys
import traceback
from datetime import datetime,timezone
from http import HTTPStatus
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    ActivityHandler,
    TurnContext,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication,
)
from botbuilder.schema import (
    Activity,
    ConversationReference,
    ActivityTypes,
    ChannelAccount,
)
import requests

from config import DefaultConfig


CONFIG = DefaultConfig()

ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD,)
# ADAPTER = BotFrameworkAdapter(SETTINGS)


async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    ##print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.now(timezone.utc),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

workspace_client = WorkspaceClient(
    host=CONFIG.DATABRICKS_HOST, token=CONFIG.DATABRICKS_TOKEN
)

genie_api = GenieAPI(workspace_client.api_client)


async def ask_genie(
    question: str, space_id: str, conversation_id: Optional[str] = None
) -> tuple[str, str]:
    try:
        loop = asyncio.get_running_loop()
        if conversation_id is None:
            initial_message = await loop.run_in_executor(
                None, genie_api.start_conversation_and_wait, space_id, question
            )
            conversation_id = initial_message.conversation_id
        else:
            
            initial_message = await loop.run_in_executor(
                None, genie_api.start_conversation_and_wait, space_id, question
            )
           
        query_result = None
        if initial_message.query_result is not None:
            query_result = await loop.run_in_executor(
                None,
                genie_api.get_message_attachment_query_result,
                #genie_api.get_message_query_result,
                space_id,
                initial_message.conversation_id,
                initial_message.message_id,
                initial_message.attachments[0].attachment_id,
           )
        message_content = await loop.run_in_executor(
            None,
            genie_api.get_message,
            space_id,
            initial_message.conversation_id,
            initial_message.message_id,
        )
        if query_result and query_result.statement_response:
            results = await loop.run_in_executor(
                None,
                workspace_client.statement_execution.get_statement,
                query_result.statement_response.statement_id,
            )

            query_description = ""
            for attachment in message_content.attachments:
                if attachment.query and attachment.query.description:
                    query_description = attachment.query.description
                    break

            return (
                json.dumps(
                    {
                        "columns": results.manifest.schema.as_dict(),
                        "data": results.result.as_dict(),
                        "query_description": query_description,
                    }
                ),
                conversation_id,
            )

        if message_content.attachments:
            for attachment in message_content.attachments:
                if attachment.text and attachment.text.content:
                    return (
                        json.dumps({"message": attachment.text.content}),
                        conversation_id,
                    )

        return json.dumps({"message": message_content.content}), conversation_id
    except Exception as e:
        logger.error(f"Error in ask_genie: {str(e)}")
        return (
            json.dumps({"error": "An error occurred while processing your request."}),
            conversation_id,
        )


def process_query_results(answer_json: Dict) -> str:
    response = ""
    if "query_description" in answer_json and answer_json["query_description"]:
        response += f"## Query Description\n\n{answer_json['query_description']}\n\n"

    if "columns" in answer_json and "data" in answer_json:
        response += "## Query Results\n\n"
        columns = answer_json["columns"]
        data = answer_json["data"]
        if isinstance(columns, dict) and "columns" in columns:
            header = "| " + " | ".join(col["name"] for col in columns["columns"]) + " |"
            separator = "|" + "|".join(["---" for _ in columns["columns"]]) + "|"
            response += header + "\n" + separator + "\n"
            for row in data["data_array"]:
                formatted_row = []
                for value, col in zip(row, columns["columns"]):
                    if value is None:
                        formatted_value = "NULL"
                    elif col["type_name"] in ["DECIMAL", "DOUBLE", "FLOAT"]:
                        formatted_value = f"{float(value):,.2f}"
                    elif col["type_name"] in ["INT", "BIGINT", "LONG"]:
                        formatted_value = f"{int(value):,}"
                    else:
                        formatted_value = str(value)
                    formatted_row.append(formatted_value)
                response += "| " + " | ".join(formatted_row) + " |\n"
        else:
            response += f"Unexpected column format: {columns}\n\n"
    elif "message" in answer_json:
        response += f"{answer_json['message']}\n\n"
    else:
        response += "No data available.\n\n"

    return response


class MyBot(ActivityHandler):
    def __init__(self):
        self.conversation_ids: Dict[str, str] = {}

    async def on_message_activity(self, turn_context: TurnContext):
        ##print("Message activity",turn_context.activity.text)
        question = turn_context.activity.text
        user_id = turn_context.activity.from_property.id
        conversation_id = self.conversation_ids.get(user_id, None)

        try:
            answer, new_conversation_id = await ask_genie(
                question, CONFIG.DATABRICKS_SPACE_ID, conversation_id
            )
            self.conversation_ids[user_id] = new_conversation_id

            answer_json = json.loads(answer)
            response = process_query_results(answer_json)

            await turn_context.send_activity(response)
        except json.JSONDecodeError:
            await turn_context.send_activity(
                "Failed to decode response from the server."
            )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await turn_context.send_activity(
                "An error occurred while processing your request."
            )

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        ##print("Members added",members_added)
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Welcome to the Databricks Genie Bot!")


BOT = MyBot()


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    try:
        response = await ADAPTER.process(req, BOT)
        ##print("Response from bot",response)
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=201)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return Response(status=500)


def init_func(argv):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.router.add_post("/api/messages", messages)
    return APP


if __name__ == "__main__":
    APP = init_func(None)
    try:
        HOST = "0.0.0.0"
        web.run_app(APP, host=HOST, port=CONFIG.PORT)
    except Exception as error:
        raise error
