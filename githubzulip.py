from errbot import BotPlugin, webhook
import zulip
import os
import requests
from urllib.parse import urlencode, quote_plus

CONFIG_TEMPLATE= {
    "IGNORED_REPOS": {
        "cern-sis": ["issues-open-science", "issues-cap", "issues-academia", "issues-scoap3", "issues-inspire", "issues"]
    }
}

class Githubzulip(BotPlugin):
    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(
                chain(
                    CONFIG_TEMPLATE.items(),
                    configuration.items()
                )
            )
        else:
            config = CONFIG_TEMPLATE
        super(PluginExample, self).configure(config)

    def get_user(self, gh):
        gh_u = ""
        client = zulip.Client(site="https://cern-rcs-sis.zulipchat.com",
                              email="errbot-bot@cern-rcs-sis.zulipchat.com",
                              api_key=os.environ["BOT_ZULIP_KEY"])
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

    def room(self, payload, event):
        stream = "infrastructure"
        topic = "errbot"
        match payload["repository"]["full_name"].split("/"):
            case ["inspirehep", repo]:
                stream = "inspire"
                topic = repo+" / "+event+" / "+str(payload[event]["number"])
            case ["hepdata", repo]:
                stream = "hepdata"
                topic = repo+" / "+event+" / "+str(payload[event]["number"])
            case ["scoap3", repo]:
                stream = "scoap3"
                topic = repo+" / "+event+" / "+str(payload[event]["number"])
            case ["cernanalysispreservation", repo]:
                stream = "cap"
                topic = repo+" / "+event+" / "+str(payload[event]["number"])
            case ["cern-sis", "digitization"]:
                stream = "digitization"
                topic = stream+" / "+event+" / "+str(payload[event]["number"])
            case ["cern-sis", "cern-academic-training"]:
                stream = "cat"
                topic = stream+" / "+event+" / "+str(payload[event]["number"])
            case ["cern-sis", "kubernetes"]:
                stream = "infrastructure"
                topic = "kubernetes / "+event+" / "+str(payload[event]["number"])
            case ["cern-sis", "workflows"]:
                stream = "scoap3"
                topic = "workflows / "+event+" / "+str(payload[event]["number"])
            case [org, repo]:
                ignored_repos = self.config["IGNORED_REPOS"]
                if repo in ignored_repos.get(org, []):
                    stream="ignore"
        return stream, topic
    
    @webhook("/github", raw=True)
    def github(self, request):
        payload = request.json
        headers = {k: v for k, v in request.headers.items() if k.startswith("X-Github")}
        headers["Content-Type"] = "application/json"
        event_header = headers["X-Github-Event"]
        BOT_API_KEY=os.environ["BOT_GITHUB_KEY"]
        # map the event headers to the field in the payload
        event_header_map = dict.fromkeys(["issues", "issue_comment"], "issue")
        event_header_map.update(dict.fromkeys(["pull_request", "pull_request_review_comment", "pull_request_review", "pull_request_review_thread"], "pull_request"))
        match event_header:
            case _:
                stream, topic = self.room(payload, event_header_map[event_header])
                if stream != "ignore":
                    params = {
                        "api_key": BOT_API_KEY,
                        "stream": stream,
                        "topic": topic
                    }
                    response = requests.post("https://cern-rcs-sis.zulipchat.com/api/v1/external/github",
                                            params=params,
                                            headers=headers,
                                            data=request.get_data())
                    self.log.info(response.status_code)
                return "OK"
