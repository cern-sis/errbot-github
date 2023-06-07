import json
import logging

import pytest

from renderers.issue import render

extra_plugin_dir = "."


@pytest.mark.parametrize(
    "action,expected",
    [
        (
            "assigned",
            "benjamin-bergia assigned this issue to:\nbenjamin-bergia",
        ),
        (
            "closed",
            "Closed by benjamin-bergia.",
        ),
        (
            "deleted",
            "Deleted by benjamin-bergia.",
        ),
        (
            "demilestoned",
            " ".join(
                [
                    "benjamin-bergia removed this issue from the milestone",
                    "[test](https://github.com/cern-sis/errbot-github/milestone/1).",
                ]
            ),
        ),
        (
            "edited",
            "".join(
                [
                    "benjamin-bergia changed the body of this issue\n",
                    "```diff\n--- \n+++ \n@@ -1 +1 @@\n",
                    "-test body\n+test body.\n```",
                ]
            ),
        ),
        (
            "labeled",
            "benjamin-bergia added label question.",
        ),
        (
            "milestoned",
            " ".join(
                [
                    "benjamin-bergia added this issue to the milestone",
                    "[test](https://github.com/cern-sis/errbot-github/milestone/1).",
                ]
            ),
        ),
        (
            "opened",
            "".join(
                [
                    "benjamin-bergia opened issue ",
                    "[1745834174](https://github.com/cern-sis/errbot-github/issues/5).",
                    "\ntest\ntest body",
                ]
            ),
        ),
        (
            "reopened",
            "Re-opened by benjamin-bergia.",
        ),
        (
            "unassigned",
            "benjamin-bergia unassigned this issue.",
        ),
        (
            "unlabeled",
            "benjamin-bergia removed label question.",
        ),
    ],
)
def test_render(action, expected, request):
    rootdir = request.config.rootdir
    file_path = rootdir / f"tests/data/issue.{action}.json"

    with open(file_path) as file:
        assert render(logging, json.load(file)) == expected
