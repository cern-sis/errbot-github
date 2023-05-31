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
        gh_u = ""
        client = self._bot.client()
        result = client.get_members()
        result = client.get_members({"client_gravatar": False})
        result = client.get_members({"include_custom_profile_fields": True})

        if result["result"] == "success":
            members = result["members"]

            for member in members:
                if "profile_data" in member:
                    if "3959" in member["profile_data"]:
                        if member["profile_data"]["3959"]["value"] == gh:
                            gh_u = member["full_name"]
        return gh_u

    def stream(self, org, repo):
        ignored_repos = self.config["IGNORED_REPOS"]
        if repo in ignored_repos.get(org, []):
            return None

        match (org, repo):
            case ("inspirehep", _):
                return "inspire"
            case ("cernanalysispreservation", _):
                return "cap"
            case ("cern-sis", "digitization"):
                return "digitization"
            case ("cern-sis", "cern-academic-training"):
                return "cat"
            case ("cern-sis", "kubernetes"):
                return "infrastructure"
            case ("cern-sis", "workflows"):
                return "scoap3"
            case ("cern-sis", _):
                return "sis"
            case (org, _):
                return org

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

    @staticmethod
    def has_been_closed(payload):
        return payload["action"] == "closed"

    @staticmethod
    def has_been_reopened(payload):
        return payload["action"] == "reopened"

    def send_notification(self, request, stream, topic):
        payload = request.json
        headers = {k: v for k, v in request.headers.items() if k.startswith("X-Github")}
        headers["Content-Type"] = "application/json"

        content = render(payload)
        if content is not None:
            client = self._bot.client()
            response = client.send_message(
                {
                    "type": "stream",
                    "to": stream,
                    "topic": topic,
                    "content": content,
                }
            )
        else:
            params = {
                "api_key": os.environ["BOT_GITHUB_KEY"],
                "stream": stream,
                "topic": topic,
            }
            response = requests.post(
                "https://cern-rcs-sis.zulipchat.com/api/v1/external/github",
                params=params,
                headers=headers,
                data=request.get_data(),
            )
            self.log.info(response.status_code)

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
