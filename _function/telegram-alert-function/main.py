import base64
import json
import os
import requests  # type: ignore
import functions_framework  # type: ignore
from datetime import datetime, timezone
import logging
import re

# Imports the Cloud Logging client library
from google.cloud import logging as cloud_logging


# --- Telegram Specific Helper ---
def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    # Order matters for some escapes (e.g., \ before other characters)
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    # Escape the escape character itself first if it's in the list (it's not by default for MarkdownV2)
    # Then escape all other characters
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


@functions_framework.cloud_event
def main(cloud_event):
    log_client = cloud_logging.Client()
    log_client.setup_logging()
    logging.basicConfig(level=logging.INFO)

    try:
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode(
            "utf-8"
        )
        logging.info(f"Pub/Sub message content: {pubsub_message}")

        message_data = json.loads(pubsub_message)
        incident = message_data.get("incident", {})

        # --- Extract common data (mostly unchanged) ---
        raw_documentation = incident.get("documentation", {})
        if isinstance(raw_documentation, dict):
            documentation_subject = raw_documentation.get("subject", "GCP Alert")
            documentation_content = raw_documentation.get("content", "No documentation content provided.")
        else:
            documentation_subject = "GCP Alert"
            documentation_content = str(raw_documentation) or "No documentation content provided."

        start_time_unix = incident.get("started_at", 0)
        start_time_str = datetime.fromtimestamp(
            start_time_unix, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")

        severity = incident.get("severity", "N/A")
        condition_name = incident.get("condition_name", "N/A")
        incident_url = incident.get("url", "")
        policy_name = incident.get("policy_name", "N/A")
        summary = incident.get("summary", "No summary provided.")
        project_id = incident.get("scoping_project_id", "N/A")

        project_link = f"https://console.cloud.google.com/?project={project_id}"
        title = documentation_subject

        policy_id = "N/A"
        condition_name_full = incident.get("condition", {}).get("name", "")
        if "/alertPolicies/" in condition_name_full:
            try:
                policy_id = condition_name_full.split("/alertPolicies/")[1].split("/")[
                    0
                ]
            except IndexError:
                logging.warning(
                    f"Could not parse policy_id from condition_name_full: {condition_name_full}"
                )

        policy_link = (
            f"https://console.cloud.google.com/monitoring/alerting/policies/{policy_id}?project={project_id}"
            if policy_id != "N/A"
            else "N/A"
        )

        documentation_content = documentation_content

        # --- Prepare Telegram Message (MarkdownV2) ---
        # Escape all dynamic string parts before inserting them into the Markdown template
        escaped_title = escape_markdown_v2(title)
        escaped_policy_name = escape_markdown_v2(policy_name)
        escaped_severity = escape_markdown_v2(severity)
        escaped_condition_name = escape_markdown_v2(condition_name)
        escaped_start_time_str = escape_markdown_v2(start_time_str)
        escaped_project_id = escape_markdown_v2(project_id)
        escaped_summary = escape_markdown_v2(summary)
        escaped_documentation_content = escape_markdown_v2(documentation_content)

        # Construct the message parts
        message_lines = [
            f"*{escaped_title}*",
            (
                f"*Policy:* [{escaped_policy_name}]({policy_link})"
                if policy_link != "N/A"
                else f"*Policy:* {escaped_policy_name}"
            ),
            f"*Severity:* {escaped_severity}",
            f"*Condition:* {escaped_condition_name}",
            f"*Start Time:* {escaped_start_time_str}",
            f"*Project:* [{escaped_project_id}]({project_link})",
            "\n*Summary:*",
            escaped_summary,
            "\n*Policy Documentation:*",
            escaped_documentation_content,
        ]
        if incident_url:
            message_lines.append(f"\n[View Incident]({incident_url})")

        telegram_message_text = "\n".join(
            line for line in message_lines if line
        )  # Filter out empty lines

        # --- Get Telegram Bot Token and Chat ID from Environment Variables ---
        bot_token = os.getenv("BOT_TOKEN")
        # You can have different chat IDs for different severities if needed
        # For simplicity, using one chat ID here, but you can adapt the MS Teams logic

        chat_id = os.getenv("GROUP_CHAT_ID")

        if not bot_token or not chat_id:
            logging.error(
                "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID (ALERT/INFO) not set."
            )
            return  # Or raise an error

        # --- Construct Telegram API URL and Payload ---
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        telegram_payload = {
            "chat_id": chat_id,
            "text": telegram_message_text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,  # Optional: set to False if you want link previews
        }

        logging.info(
            f"Sending to Telegram Chat ID {chat_id}. Payload: {telegram_payload}"
        )

        # --- Send the payload to Telegram ---
        response = requests.post(telegram_api_url, json=telegram_payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

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
