from errbot import BotPlugin, webhook
import zulip
import json
import os
import requests
from urllib.parse import urlencode, quote_plus


class Githubzulip(BotPlugin):
    """
    Plugin to recieve webhooks from Github and route it to Zulip
    """
    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Githubzulip, self).activate()

    def deactivate(self):
        """
        Triggers on plugin deactivation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Githubzulip, self).deactivate()

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {
            "EXAMPLE_KEY_1": "Example value",
            "EXAMPLE_KEY_2": ["Example", "Value"],
        }

    def check_configuration(self, configuration):
        """
        Triggers when the configuration is checked, shortly before activation

        Raise a errbot.ValidationException in case of an error

        You should delete it if you're not using it to override any default behaviour
        """
        super(Githubzulip, self).check_configuration(configuration)

    def callback_connect(self):
        """
        Triggers when bot is connected

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_botmessage(self, message):
        """
        Triggered for every message that comes from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass
    def get_user(self, gh):
        gh_u = ""
        client = zulip.Client(site="https://cern-rcs-sis.zulipchat.com",
                              email="errbot-bot@cern-rcs-sis.zulipchat.com",
                              api_key=os.environ['BOT_ZULIP_KEY'])
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

        return stream, topic
    
    @webhook('/github', raw=True)
    def github(self, request):
        payload = request.json
        headers = {k: v for k, v in request.headers.items() if k.startswith('X-Github')}
        headers['Content-Type'] = 'application/json'
        event_header = headers['X-Github-Event']
        BOT_API_KEY=os.environ['BOT_GITHUB_KEY']
        # map the event headers to the field in the payload
        event_header_map = dict.fromkeys(['issues', 'issue_comment'], 'issue')
        event_header_map.update(dict.fromkeys(['pull_request', 'pull_request_review_comment', 'pull_request_review', 'pull_request_review_thread'], 'pull_request'))
        match event_header:
            # do custom notifications for special events
            case "issue_comment":
                gh_uid = payload["issue"]["user"]["login"]
                stream, topic = self.room(payload, event_header_map[event_header])
                user = self.get_user(gh_uid)
                self.send(
                    self.build_identifier(f"#{{{{{stream}}}}}*{{{{{topic}}}}}"),
                    '@**{0}** {1} issue#{2} {3} {4}'.format(user, payload["action"], payload["issue"]["number"], payload["issue"]["title"], payload["issue"]["html_url"]),
                )
            # use zulip github integration for generic messages
            case _:
                stream, topic = self.room(payload, event_header_map[event_header])
                params = {
                    'api_key': BOT_API_KEY,
                    'stream': stream,
                    'topic': topic
                }
                response = requests.post("https://cern-rcs-sis.zulipchat.com/api/v1/external/github",
                                         params=params,
                                         headers=headers,
                                         data=request.get_data())
                self.log.info(response.status_code)
                self.log.info(response.text)
