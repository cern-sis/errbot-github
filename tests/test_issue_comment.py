import json
import logging

import pytest

from renderers import render

extra_plugin_dir = "."


@pytest.mark.parametrize(
    "action,expected",
    [
        (
            "created",
            "".join(
                [
                    ":pen: benjamin-bergia [commented]",
                    "(https://github.com/cern-sis/kubernetes",
                    "/issues/718#issuecomment-1580330894):\n",
                    "```quote\nJust a test\n```",
                ]
            ),
        ),
        (
            "edited",
            "".join(
                [
                    ":pencil: benjamin-bergia edited a comment:\n",
                    "```diff\n--- \n+++ \n@@ -1 +1 @@\n-Just a test\n",
                    "+Just an edited test\n```",
                ]
            ),
        ),
        ("deleted", ":wastebasket: benjamin-bergia deleted a comment."),
    ],
)
def test_render(action, expected, request):
    rootdir = request.config.rootdir
    file_path = rootdir / f"tests/data/issue_comment.{action}.json"

    with open(file_path) as file:
        assert render(logging, "issue_comment", json.load(file)) == expected
