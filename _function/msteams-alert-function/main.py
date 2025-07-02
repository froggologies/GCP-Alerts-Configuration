import base64
import json
import os
import requests  # type: ignore
import functions_framework  # type: ignore
from datetime import datetime, timezone
import logging


# Imports the Cloud Logging client library
from google.cloud import logging as cloud_logging


@functions_framework.cloud_event
def main(cloud_event):
    # Instantiates a client
    log_client = cloud_logging.Client()

    # Retrieves a Cloud Logging handler based on the environment
    # you're running in and integrates the handler with the
    # Python logging module. By default this captures all logs
    # at INFO level and higher
    log_client.setup_logging()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Decode the incoming Pub/Sub message
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode(
            "utf-8"
        )

        logging.info(
            f"Pub/Sub message content: {pubsub_message}"
        )  # Log the message content

        # Parse the message as JSON
        message_data = json.loads(pubsub_message)

        # Extract relevant fields for the message text
        incident = message_data.get("incident", {})
        documentation = incident.get("documentation", {})
        start_time = datetime.fromtimestamp(
            incident.get("started_at", 0), tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Extract details
        severity = incident.get("severity", {})
        condition_name = incident.get("condition_name", {})
        incident_url = incident.get("url", {})
        policy_name = incident.get("policy_name", {})
        summary = incident.get("summary", {})
        project_id = incident.get("scoping_project_id", {})

        project_link = f"https://console.cloud.google.com/?project={project_id}"

        title = documentation.get("subject", {})

        # Extract policy ID from condition.name
        condition_name_full = incident.get("condition", {}).get("name", "")
        policy_id = condition_name_full.split("/alertPolicies/")[1].split("/")[0]

        # Generate the policy link
        policy_link = f"https://console.cloud.google.com/monitoring/alerting/policies/{policy_id}?project={project_id}"

        # Extract documentation
        documentation_content = documentation.get(
            "content", "No documentation content provided"
        )

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
                                "text": f"**{title}**",
                                "wrap": True,
                                "size": "medium",
                                "weight": "bolder",
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Policy:** [{policy_name}]({policy_link})",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Severity:** {severity}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Condition:** {condition_name}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Start Time:** {start_time}",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Project:** [{project_id}]({project_link})",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Summary:**",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": summary,
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
                                "text": documentation_content,
                                "wrap": True,
                            },
                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "View Incident",
                                        "url": incident_url,
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

        logging.info(f"Constructed payload successfully: {payload}")

        # Determine the webhook URL based on severity
        webhook_url = (
            os.getenv("WEBHOOK_URL_ALERT")
            if severity in ["Critical", "Warning"]
            else os.getenv("WEBHOOK_URL_INFO")
        )

        # Send the payload to the webhook
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

        logging.info(f"Successfully sent data to webhook: {response.status_code}")
    except Exception as e:
        logging.error(f"Error processing Pub/Sub message: {e}")
