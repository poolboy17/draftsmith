from output import write_output


def test_write_output_md(tmp_path):
    content = "# Title\n\nHello"
    dest = tmp_path / "out.md"
    write_output(content, str(dest), "md")
    assert dest.read_text(encoding="utf-8").startswith("# Title")


def test_write_output_html(tmp_path):
    content = "# Title\n\nHello"
    dest = tmp_path / "out.html"
    write_output(content, str(dest), "html")
    text = dest.read_text(encoding="utf-8")
    assert "<html>" in text and "</html>" in text
