def codeblock(*args, lang=""):
    return "\n".join(
        [
            f"```{lang}",
            *args,
            "```",
        ]
    )


def quoteblock(*args):
    return codeblock(
        *args,
        lang="quote",
    )


def diffblock(*args):
    return codeblock(
        *args,
        lang="diff",
    )


def pythonblock(*args):
    return codeblock(
        *args,
        lang="python",
    )


def lines(*args):
    return "\n".join(args)


def link(title, url):
    return f"[{title}]({url})"
