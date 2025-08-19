import base64
import json
import logging
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

import functions_framework  # type: ignore
import requests  # type: ignore

# Imports the Cloud Logging client library
from google.cloud import logging as cloud_logging


# Data Extraction Helper
def extract_incident_data(message_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Parses the full GCP Alerting webhook payload and extracts key information from the 'incident' field.

    Args:
        message_data: The full decoded and parsed JSON payload from the Pub/Sub message.

    Returns:
        A dictionary containing structured and processed information from the incident.
    """

    incident = message_data.get("incident")

    # Extract documentation
    if message_data.get("version") == "test":
        title = "Test Alert"
        documentation_content = incident.get("documentation")
    else:
        title = incident.get("documentation", {}).get("subject", "GCP Alert")
        documentation_content = incident.get("documentation", {}).get("content", "")

    policy_name = incident.get("policy_name")

    policy_id = ""
    condition_full_name = incident.get("condition").get("name")
    if "/alertPolicies/" in condition_full_name:
        policy_id = condition_full_name.split("/alertPolicies/")[1].split("/")[0]

    project_id = incident.get("scoping_project_id")
    policy_link = (
        f"https://console.cloud.google.com/monitoring/alerting/policies/{policy_id}?project={project_id}"
        if policy_id != ""
        else "https://policy-not-found"
    )

    severity = incident.get("severity", "No severity")
    condition_name = incident.get("condition_name")

    start_time_unix = incident.get("started_at", 0)
    start_time_str = datetime.fromtimestamp(start_time_unix, tz=timezone(timedelta(hours=7))).strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    project_link = f"https://console.cloud.google.com/?project={project_id}"

    summary = incident.get("summary")

    incident_url = incident.get("url")

    return {
        "title": title,
        "policy_name": policy_name,
        "policy_link": policy_link,
        "severity": severity,
        "condition_name": condition_name,
        "start_time_str": start_time_str,
        "project_id": project_id,
        "project_link": project_link,
        "summary": summary,
        "documentation_content": documentation_content,
        "incident_url": incident_url,
    }


# Telegram Specific Helper
def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    # Characters that need escaping in Telegram MarkdownV2
    special_chars = "_*[]()~`>#+-=|{}.! "

    # Create a regex pattern to match any of these characters
    pattern = f"[{re.escape(special_chars)}]"

    # Replace each special char with a backslash + the char
    escaped_text = re.sub(pattern, lambda m: "\\" + m.group(0), text)

    return escaped_text


@functions_framework.cloud_event
def main(cloud_event):
    # Instantiates a client
    log_client = cloud_logging.Client()
    log_client.setup_logging()

    pubsub_message = ""  # Initialize to ensure it's available in error logs
    try:
        # Decode the incoming Pub/Sub message
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode(
            "utf-8"
        )
        logging.info(f"Pub/Sub message content: {pubsub_message}")

        # Parse the message as JSON
        message_data = json.loads(pubsub_message)

        # --- Extract data using the helper function, passing the whole payload ---
        details = extract_incident_data(message_data)

        # --- Prepare Telegram Message (MarkdownV2) ---
        # Escape all dynamic string parts before inserting them into the Markdown template
        title = escape_markdown_v2(details["title"])
        policy_name = escape_markdown_v2(details["policy_name"])
        severity = escape_markdown_v2(details["severity"])
        condition_name = escape_markdown_v2(details["condition_name"])
        start_time_str = escape_markdown_v2(details["start_time_str"])
        project_id = escape_markdown_v2(details["project_id"])
        summary = escape_markdown_v2(details["summary"])
        documentation_content = escape_markdown_v2(details["documentation_content"])

        # Construct the message parts
        message_lines = [
            f"*{title}*\n",
            (
                f"*Policy:* [{policy_name}]({details['policy_link']})"
                if details["policy_link"] != "https://policy-not-found"
                else f"*Policy:* {policy_name}"
            ),
            f"*Severity:* {severity}",
            f"*Condition:* {condition_name}",
            f"*Start Time:* {start_time_str}",
            f"*Project:* [{project_id}]({details['project_link']})",
            "\n*Summary:*",
            summary,
            "\n*Policy Documentation:*",
            documentation_content,
            f"\n[View incident]({details['incident_url']})",
        ]

        telegram_message_text = "\n".join(
            line for line in message_lines if line
        )  # Filter out empty lines

        # --- Get Telegram Bot Token and Chat ID from Environment Variables ---
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("GROUP_CHAT_ID")

        if not bot_token or not chat_id:
            logging.error("BOT_TOKEN or GROUP_CHAT_ID environment variables not set.")
            return

        # --- Construct Telegram API URL and Payload ---
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        telegram_payload = {
            "chat_id": chat_id,
            "text": telegram_message_text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        }

        logging.info(
            f"Sending to Telegram Chat ID {chat_id}. Payload: {telegram_payload}"
        )

        # --- Send the payload to Telegram ---
        response = requests.post(telegram_api_url, json=telegram_payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        logging.info(
            f"Successfully sent data to Telegram: {response.status_code} - {response.text}"
        )

    except json.JSONDecodeError as e:
        logging.error(
            f"Error decoding Pub/Sub message JSON: {e}. Message: {pubsub_message}"
        )
    except requests.exceptions.HTTPError as e:
        logging.error(
            f"HTTP error sending to Telegram: {e}. Response: {e.response.text if e.response else 'No response'}"
        )
    except Exception as e:
        logging.error(
            f"Error processing Pub/Sub message for Telegram: {e}", exc_info=True
        )