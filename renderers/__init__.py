def render(payload):
    if "issue" in payload:
        from .issue import render

        render(payload)
    else:
        return None
