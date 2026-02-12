def render_final_page(html: str, css: str) -> str:
    """Inline CSS into the HTML page inside a <style> tag before </head>."""
    style_block = f"<style>\n{css}\n</style>"

    head_close = html.lower().find("</head>")
    if head_close == -1:
        return f"<!DOCTYPE html>\n<html>\n<head>\n{style_block}\n</head>\n<body>\n{html}\n</body>\n</html>"

    return html[:head_close] + style_block + "\n" + html[head_close:]
