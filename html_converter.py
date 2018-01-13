from __future__ import unicode_literals


def create_html_page(content):
    html = """
<html>
<head>
    <meta charset="utf-8" />
</head>
<body>
    {}
</body>
</html>
    """.format(content)
    return html


def create_html_toc(contents):
    html = '<ul>'
    for page in contents:
        html += '<li>'
        html += '<a href="{}">{}</a>'.format(page.content, page.label)
        if len(page.children) > 0:
            html += create_html_toc(page.children)
        html += '</li>'

    html += '</ul>'
    return html
