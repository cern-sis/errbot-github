import json

import pytest

pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "."


@pytest.mark.parametrize(
    "stream,topic,expected",
    [
        ("scoap3", "whatever", True),
        ("inspire", "inspire-prod", True),
        ("inspire", "inspire-qa", False),
        ("infrastructure", "whichever", False),
    ],
)
def test_filter_senders(testbot, stream, topic, expected):
    with open("tests/data/issue_comment.edited.json") as file:
        payload = json.load(file)
        plugin = testbot.bot.plugin_manager.get_plugin_obj_by_name("Github")
        plugin.configure(
            {
                "IGNORED_SENDERS": {
                    "benjamin-bergia": {
                        "scoap3": "*",
                        "inspire": ["inspire-prod"],
                    },
                },
            }
        )

        assert plugin.filter_sender(stream, topic, payload) is expected
