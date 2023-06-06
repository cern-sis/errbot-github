from difflib import unified_diff

from .markdown import diffblock, lines, quoteblock


def render(logger, payload):
    user = payload["sender"]["login"]
    comment = payload["comment"]
    action = payload["action"]

    logger.info(f"Issue comment has been {action}")

    match action:
        case "created":
            return lines(
                f":pen: {user} [commented]({comment['html_url']}):",
                quoteblock(comment["body"]),
            )

        case "deleted":
            return f":wastebasket: {user} deleted a comment."

        case "edited":
            old = payload["changes"]["body"]["from"].split("\n")
            new = comment["body"].split("\n")

            return lines(
                f":pencil: {user} edited a comment:",
                diffblock(*unified_diff(old, new, lineterm="")),
            )
