import base64
import json
import logging
import os
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
    start_time_str = datetime.fromtimestamp(
        start_time_unix, tz=timezone(timedelta(hours=7))
    ).strftime("%Y-%m-%d %H:%M:%S %Z")

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

        # Extract data using the helper function, passing the whole payload
        details = extract_incident_data(message_data)

        # Construct the payload
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"**{details["title"]}**",
                                "wrap": True,
                                "size": "medium",
                                "weight": "bolder",
                            },
                            {
                                "type": "TextBlock",
                                "text": (
                                    f"*Policy:* [{details["policy_name"]}]({details["policy_link"]})"
                                    if details["policy_link"]
                                    != "https://policy-not-found"
                                    else f"*Policy:* {details["policy_name"]}"
                                ),
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Severity:** {details["severity"]}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Condition:** {details["condition_name"]}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Start time:** {details["start_time_str"]}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Project:** [{details["project_id"]}]({details["project_link"]})",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Summary:**",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": details["summary"],
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Policy documentation**",
                                "wrap": True,
                                "size": "medium",
                                "weight": "bolder",
                                "separator": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": details["documentation_content"],
                                "wrap": True,
                            },
                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "View Incident",
                                        "url": details["incident_url"],
                                    }
                                ],
                            },
                        ],
                    },
                }
            ],
        }

        # Remove None values in the payload body
        payload["attachments"][0]["content"]["body"] = [
            item
            for item in payload["attachments"][0]["content"]["body"]
            if item is not None
        ]

        # Get MSTeams webhook URL from 
        webhook_url = os.getenv("WEBHOOK_URL")

        if not webhook_url:
            logging.error("WEBHOOK_URL environment variables not set.")
            return

        logging.info(
            f"Sending to Microsoft Teams webhook URL {webhook_url}. Payload: {payload}"
        )

        # Send the payload to the webhook
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        logging.info(
            f"Successfully sent data to MSTeams webhook: {response.status_code} - {response.text}"
        )

    except json.JSONDecodeError as e:
        logging.error(
            f"Error decoding Pub/Sub message JSON: {e}. Message: {pubsub_message}"
        )
    except requests.exceptions.HTTPError as e:
        logging.error(
            f"HTTP error sending to MSTeams webhook: {e}. Response: {e.response.text if e.response else 'No response'}"
        )
    except Exception as e:
        logging.error(
            f"Error processing Pub/Sub message for MSTeams webhook: {e}", exc_info=True
        )
