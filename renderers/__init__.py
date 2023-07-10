from . import issue, issue_comment


def render(logger, event, payload):
    match event:
        case "issue_comment":
            return issue_comment.render(logger, payload)

        case "issue":
            return issue.render(logger, payload)

    return None
