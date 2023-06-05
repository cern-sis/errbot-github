from . import issue, issue_comment


def render(logger, payload):
    keys = payload.keys()

    if keys & {"issue", "comment"}:
        logger.info("Rendering an issue_comment event")
        return issue_comment.render(logger, payload)
    elif keys & {"issue"}:
        logger.info("Rendering an issue event")
        return issue.render(logger, payload)
    else:
        return None
