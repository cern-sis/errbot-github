def codeblock(content, language=""):
    return "\n".join(
        f"```{language}",
        content,
        "```",
    )
