import os
from itertools import chain

import requests
from errbot import BotPlugin, webhook

from renderers import render

CONFIG_TEMPLATE = {
    "IGNORED_REPOS": {
        "cern-sis": [
            "issues-open-science",
            "issues-cap",
            "issues-academia",
            "issues-scoap3",
            "issues-inspire",
            "issues",
        ],
    },
    "STREAMS": {
        "inspirehep": {"*": "inspire"},
        "cernanalysispreservation": {"*", "cap"},
        "cern-sis": {
            "digitization": "digitization",
            "cern-academic-training": "cat",
            "kubernetes": "infrastructure",
            "workflows": "scoap3",
            "*": "sis",
        },
    },
    "IGNORED_SENDERS": {
        "codecov-commenter": {
            "scoap3": "*",
        },
    },
}


class Github(BotPlugin):
    @staticmethod
    def get_configuration_template():
        return CONFIG_TEMPLATE

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(), configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(Github, self).configure(config)

    def get_user(self, gh):
        client = self._bot.client()
        result = client.get_members(
            {
                "client_gravatar": False,
                "include_custom_profile_fields": True,
            }
        )

        if result["result"] == "success":
            return self.get_github_id(result["members"], gh)

    @staticmethod
    def get_github_id(members, gh):
        return next(
            [
                member["full_name"]
                for member in members
                if member.get("profile_data", {}).get("3959", {}).get("value") == gh
            ],
            None,
        )

    def stream(self, org, repo):
        ignored_repos = self.config["IGNORED_REPOS"]
        streams = self.config["STREAMS"]

        if repo in ignored_repos.get(org, []):
            return None

        if org not in streams:
            return org

        if repo not in streams[org]:
            return streams[org]["*"]

        return streams[org][repo]

    @staticmethod
    def topic(repo, ref):
        return f"{repo}/{ref}"

    def room(self, payload, event_header):
        item = self.item(event_header)
        if item is None:
            return None, None

        org, repo = payload["repository"]["full_name"].split("/")
        stream = self.stream(org, repo)
        ref = str(payload[item]["number"])
        topic = self.topic(repo, ref)
        return stream, topic

    @staticmethod
    def item(event):
        if event.startswith("issue"):
            return "issue"
        elif event.startswith("pull_request"):
            return "pull_request"
        else:
            return None

    def filter_sender(self, stream, topic, payload):
        user = payload["sender"]["login"]
        filtered_topics = self.config["IGNORED_SENDERS"].get(user, {}).get(stream, {})

        if filtered_topics == "*" or topic in filtered_topics:
            return True
        else:
            return False

    def send_notification(self, request, stream, topic):
        event = request.headers["X-Github-Event"]
        payload = request.json

        if self.filter_sender(stream, topic, payload):
            return

        match render(self.log, event, payload):
            case False:
                # Dropping notification for this event
                self.log.info("Dropping Github webhook event")

            case None:
                # Use the default GH integration from Zulip
                headers = {
                    k: v for k, v in request.headers.items() if k.startswith("X-Github")
                }
                headers["Content-Type"] = "application/json"
                params = {
                    "api_key": os.environ["BOT_GITHUB_KEY"],
                    "stream": stream,
                    "topic": topic,
                }
                requests.post(
                    "https://cern-rcs-sis.zulipchat.com/api/v1/external/github",
                    params=params,
                    headers=headers,
                    data=request.get_data(),
                )
                self.log.info(
                    "Forwarding Github webhook event to the github integration"
                )

            case content:
                # Use our own template for this event
                client = self._bot.client
                client.send_message(
                    {
                        "type": "stream",
                        "to": stream,
                        "topic": topic,
                        "content": content,
                    }
                )
                self.log.info("Sending Github webhook event notification")

    @webhook("/github", raw=True)
    def github(self, request):
        payload = request.json
        event_header = request.headers["X-Github-Event"]

        stream, topic = self.room(payload, event_header)
        if stream is None:
            return None

        if payload["action"] == "reopened":
            archive_topic = self.get_plugin("Archive").archived_topic(stream, topic)
            self.get_plugin("Archive").restore_topic(archive_topic)

        self.send_notification(request, stream, topic)

        if payload["action"] == "closed":
            self.get_plugin("Archive").archive_topic(stream, topic)
