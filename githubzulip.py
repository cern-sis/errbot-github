from errbot import BotPlugin, webhook


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

    @webhook('/github/issues', form_param = 'payload')
    def github_issues(self, payload):
            for room in self.rooms():
                self.log.debug("%s room\n", room)
                self.send( 
                    self.build_identifier("#{{{{{stream}}}}}*{{{{{topic}}}}}".format(stream=room, topic=payload['repository']['full_name'])),
                    '{0} {1} issue#{2} {3} {4}'.format(payload['issue']['user']['login'], payload['action'], payload['issue']['number'], payload['issue']['title'], payload['issue']['html_url']),
                )

    @webhook('/github/pr', form_param = 'payload')
    def github_pr(self, payload):
            for room in self.rooms():
                self.send(
                    self.build_identifier("#{{{{{stream}}}}}*{{{{{topic}}}}}".format(stream=room, topic=payload['repository']['full_name'])),
                    '{0} {1} Pull Request#{2} {3} {4}'.format(payload['pull_request']['user']['login'], payload['action'], payload['pull_request']['number'], payload['pull_request']['title'], payload['pull_request']['html_url']),
                )

