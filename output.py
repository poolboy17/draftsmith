import markdown


def write_output(content: str, filepath: str, fmt: str = "md") -> None:
    if fmt == "html":
        html_body = markdown.markdown(content)
        html = f"<!DOCTYPE html><html><body>{html_body}</body></html>"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
