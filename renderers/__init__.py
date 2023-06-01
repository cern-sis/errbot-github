from . import issue


def render(logger, payload):
    if "issue" in payload:
        logger.info("Rendering an issue event")
        issue.render(logger, payload)
    else:
        return None
