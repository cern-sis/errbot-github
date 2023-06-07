from renderers import markdown as md

extra_plugin_dir = "."


def test_codeblock():
    assert md.codeblock("a", "b", "c") == "```\na\nb\nc\n```"
    assert md.codeblock("a", "b", "c", lang="test") == "```test\na\nb\nc\n```"


def test_quoteblock():
    assert md.quoteblock("a", "b", "c") == "```quote\na\nb\nc\n```"


def test_diffblock():
    assert md.diffblock("a", "b", "c") == "```diff\na\nb\nc\n```"


def test_pythonblock():
    assert md.pythonblock("a", "b", "c") == "```python\na\nb\nc\n```"


def test_lines():
    assert (
        md.lines(
            "a",
            "b",
            "c",
        )
        == "a\nb\nc"
    )


def test_link():
    assert (
        md.link(
            "title",
            "https://test.test",
        )
        == "[title](https://test.test)"
    )
