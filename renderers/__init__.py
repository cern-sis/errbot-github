import issue


def render(payload):
    if "issue" in payload:
        issue.render(payload)
    else:
        return None
