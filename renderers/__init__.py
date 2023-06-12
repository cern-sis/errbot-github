from . import issue, issue_comment


def render(logger, event, payload):
    logger.info(f"Renderer received {event}")

    match event:
        case "issue_comment":
            logger.info("Rendering an issue_comment event")
            return issue_comment.render(logger, payload)

        case "issue":
            logger.info("Rendering an issue event")
            return issue.render(logger, payload)

    return None
