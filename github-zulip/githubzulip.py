from errbot import BotPlugin, webhook
import zulip
import json
import os


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
        gh_u = "non"
        # Load the Zulip API configuration from the .zuliprc file
        client = zulip.Client(site="https://cern-rcs-sis.zulipchat.com",
                              email=os.environ['BOT_ZULIP_EMAIL'],
                              api_key=os.environ['BOT_ZULIP_KEY'])

        # Get all users in the realm
        result = client.get_members()
        # You may pass the `client_gravatar` query parameter as follows:
        result = client.get_members({"client_gravatar": False})
        # You may pass the `include_custom_profile_fields` query parameter as follows:
        result = client.get_members({"include_custom_profile_fields": True})

        if result["result"] == "success":
            members = result["members"]

            for member in members:
                if "profile_data" in member:
                    if "3959" in member["profile_data"]:
                        if member["profile_data"]["3959"]["value"] == gh:
                            gh_u = member["full_name"]
        return gh_u

    @webhook('/github', raw=True)
    def github_issues(self, request):
            event_header = request.headers.get('X-Github-Event')
            payload = request.form.get('payload')
            payload_json = json.loads(payload)
            event = self.get_zulip_event_name(event_header, payload_json)
            body_fn = self.EVENT_FUNCTION_MAPPER[event]
            body =  body_fn(self, payload_json)

    def get_zulip_event_name(self, event_header, payload):
        if event_header in list(self.EVENT_FUNCTION_MAPPER.keys()):
            return event_header

    def get_issue_body(self, payload):
        gh_uid = payload["issue"]["user"]["login"]
        user = self.get_user(gh_uid)
        for room in self.rooms():
            self.send(
                self.build_identifier("#{{{{{stream}}}}}*{{{{{topic}}}}}".format(stream=room, topic=payload["repository"]["full_name"])),
                '@**{0}** {1} issue#{2} {3} {4}'.format(user, payload["action"], payload["issue"]["number"], payload["issue"]["title"], payload["issue"]["html_url"]),
            )

    def get_pullrequest_body(self, payload):
        gh_uid = payload["pull_request"]["user"]["login"]
        user = self.get_user(gh_uid)
        for room in self.rooms():
            self.send(
                self.build_identifier("#{{{{{stream}}}}}*{{{{{topic}}}}}".format(stream=room, topic=payload["repository"]["full_name"])),
                '@**{0}** {1} pull request#{2} {3} {4}'.format(user, payload["action"], payload["pull_request"]["number"], payload["pull_request"]["title"], payload["pull_request"]["html_url"]),
            )

    EVENT_FUNCTION_MAPPER = {
        "issues": get_issue_body,
        "pull_request": get_pullrequest_body,
    }
