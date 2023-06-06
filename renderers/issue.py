from difflib import unified_diff

from .markdown import diffblock, lines, link


def render(logger, payload):
    user = payload["sender"]["login"]
    issue = payload["issue"]
    action = payload["action"]

    logger.info(f"Issue has been {action}")

    match action:
        case "assigned":
            return lines(
                f"{user} assigned this issue to:",
                *[a["login"] for a in payload["assignees"]],
            )

        case "closed":
            return f"Closed by {user}."

        case "deleted":
            return f"Deleted by {user}."

        case "demilestoned":
            milestone = issue["milestone"]
            ln = link(milestone["title"], milestone["html_url"])

            return f"{user} removed this issue from the milestone {ln}."

        case "edited":
            changes = payload["changes"]

            if "body" in changes:
                old = changes["body"]["from"].split("\n")
                new = issue["body"].split("\n")

                return lines(
                    f"{user} changed the body of this issue",
                    diffblock(
                        *unified_diff(old, new, lineterm=""),
                    ),
                )

            elif "title" in changes:
                old = changes["title"]["from"].split("\n")
                new = issue["title"].split("\n")

                return lines(
                    f"{user} changed the title of this issue",
                    diffblock(
                        *unified_diff(old, new, lineterm=""),
                    ),
                )

            return None

        case "labeled":
            return f"{user} added label {payload['label']['name']}."

        case "locked":
            return False

        case "milestoned":
            milestone = issue["milestone"]
            ln = link(
                milestone["title"],
                milestone["html_url"],
            )

            return f"{user} added this issue to the milestone {ln}."

        case "opened":
            ln = link(
                issue["id"],
                issue["html_url"],
            )

            return lines(
                f"{user} opened issue {ln}.",
                f"{issue['title']}",
                f"{issue['body']}",
            )

        case "pinned":
            return False

        case "reopened":
            return f"Re-opened by {user}."

        case "transferred":
            return None

        case "unassigned":
            return f"{user} unassigned this issue."

        case "unlabeled":
            return f"{user} removed label {payload['label']['name']}."

        case "unlocked":
            return False

        case "unpinned":
            return False
