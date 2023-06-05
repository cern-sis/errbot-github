from difflib import unified_diff
from inspect import cleandoc

from .markdown import codeblock


def render(logger, payload):
    user = payload["sender"]["login"]
    comment = payload["comment"]
    action = payload["action"]

    logger.info(f"Issue comment has been {action}")

    match action:
        case "created":
            return cleandoc(
                f"""\
                :pen: {user} [commented]({comment["html_url"]}):
                {codeblock(comment["body"], "quote")}
                """
            )

        case "deleted":
            return f" :wastebasket: {user} deleted a comment."

        case "edited":
            old = payload["changes"]["body"]["from"].split("\n")
            new = comment["body"].split("\n")

            return "\n".join(
                [
                    f":pencil: {user} edited a comment:",
                    codeblock(*unified_diff(old, new, lineterm=""), "quote"),
                ]
            )
