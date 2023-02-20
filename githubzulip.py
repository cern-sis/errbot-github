import os
from itertools import chain

import requests
import zulip
from errbot import BotPlugin, webhook

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


class Githubzulip(BotPlugin):
    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(), configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(Githubzulip, self).configure(config)

    def get_user(self, gh):
        gh_u = ""
        client = zulip.Client(
            site="https://cern-rcs-sis.zulipchat.com",
            email="errbot-bot@cern-rcs-sis.zulipchat.com",
            api_key=os.environ["BOT_ZULIP_KEY"],
        )
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
        match (org, repo):
            case ("inspirehep", _):
                return "inspire"
            case ("hepdata", _):
                return "hepdata"
            case ("scoap3", _):
                return "scoap3"
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
            case (org, _):
                ignored_repos = self.config["IGNORED_REPOS"]
                if repo in ignored_repos.get(org, []):
                    return None
                else:
                    return org

    def topic(self, repo, item, ref):
        return f"{repo} / {item} / {ref}"

    def room(self, payload, event_header):
        item = self.item(event_header)
        if item is None:
            return None, None

        org, repo = payload["repository"]["full_name"].split("/")
        stream = self.stream(org, repo)
        ref = str(payload[item]["number"])
        topic = self.topic(repo, item, ref)
        return stream, topic

    def item(self, event):
        if event.startswith("issue"):
            return "issue"
        elif event.startswith("pull_request"):
            return "pull_request"
        else:
            return None

    @webhook("/github", raw=True)
    def github(self, request):
        payload = request.json
        headers = {k: v for k, v in request.headers.items() if k.startswith("X-Github")}
        headers["Content-Type"] = "application/json"
        event_header = headers["X-Github-Event"]

        stream, topic = self.room(payload, event_header)
        if stream is None:
            return None

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
