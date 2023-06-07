from . import issue, issue_comment


def render(logger, request):
    payload = request.json

    match request.headers["X-Github-Event"]:
        case "issue_comment":
            logger.info("Rendering an issue_comment event")
            return issue_comment.render(logger, payload)

        case "issue":
            logger.info("Rendering an issue event")
            return issue.render(logger, payload)

    return None
