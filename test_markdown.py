from renderers import markdown

extra_plugin_dir = "."


def test_codeblock():
    assert markdown.codeblock("a", "b", "c") == "```\na\nb\nc\n```"
