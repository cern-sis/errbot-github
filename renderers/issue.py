from difflib import unified_diff
from textwrap import dedent


def render(logger, payload):
    user = payload["sender"]["login"]
    issue = payload["issue"]
    action = payload["action"]

    logger.info(f"Issue has been {action}")

    match action:
        case "assigned":
            return dedent(
                f"""\
                {user} assigned this issue to:
                {[a['login'] for a in payload['assignees']]}.
                """
            )

        case "closed":
            return f"Closed by {user}."

        case "deleted":
            return f"Deleted by {user}."

        case "demilestoned":
            milestone = issue["milestone"]
            link = f"[{milestone['title']}]({milestone['html_url']})"

            return dedent(
                f"""\
                {user} removed this issue from the milestone {link}.
                """
            )

        case "edited":
            changes = payload["changes"]

            if "body" in changes:
                old = changes["body"]["from"]
                new = issue["body"]
                diff = "".join(unified_diff(old, new))

                return dedent(
                    f"""\
                    {user} changed the body of this issue
                    ```patch
                    {diff}
                    ```
                    """
                )

            elif "title" in changes:
                old = changes["title"]["from"]
                new = issue["title"]
                diff = "".join(unified_diff(old, new))

                return dedent(
                    f"""\
                    {user} changed the title of this issue
                    ```patch
                    {diff}
                    ```
                    """
                )

            return None

        case "labeled":
            return f"{user} added label {issue['label']['name']}."

        case "locked":
            return False

        case "milestoned":
            milestone = issue["milestone"]
            link = f"[{milestone['title']}]({milestone['html_url']})"

            return dedent(
                f"""\
                {user} added this issue to the milestone {link}.
                """
            )

        case "opened":
            return dedent(
                f"""\
                {user} opened issue [{issue['id']}]({issue['html_url']}).
                {issue['title']}
                {issue['body']}
                """
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
            return f"{user} removed label {issue['label']['name']}."

        case "unlocked":
            return False

        case "unpinned":
            return False
