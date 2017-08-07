from local_html.html_base import HtmlElement
from utils import getparam


class html(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='html', **kwargs)


class comment(HtmlElement):
    def __init__(self, lines):
        super().__init__(single_line=len(lines) > 1)
        if isinstance(lines, list):
            for line in lines:
                self.child(line)
        else:
            self.child(lines)

    def format_open(self, cfg):
        cfg.startline('<!-- ')
        if not self.single_line:
            cfg.endline()

    def format_close(self, cfg):
        if not self.single_line:
            cfg.writeline('-->')
        else:
            cfg.endline(' -->')


class head(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='head', **kwargs)


class link(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='link', single_line=True, close_tag=False, **kwargs)


class script(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='script', **kwargs)


class meta(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='meta', single_line=True, close_tag=False, **kwargs)


class title(HtmlElement):
    def __init__(self, title, **kwargs):
        super().__init__(tag='title', single_line=True, **kwargs)
        self.child(title)


class style(HtmlElement):
    def __init__(self, **kwargs):
        styles = getparam(kwargs, 'styles', None, True)
        super().__init__(tag='style', **kwargs)
        if styles is not None:
            for line in styles:
                self.child(line)


class body(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='body', **kwargs)


class div(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='div', **kwargs)


class span(HtmlElement):
    def __init__(self, **kwargs):
        if 'single_line' not in kwargs:
            kwargs['single_line'] = True
        super().__init__(tag='span', **kwargs)


class i(HtmlElement):
    def __init__(self, icon, **kwargs):
        super().__init__(tag='i', single_line=True, **kwargs)
        self.child(icon)


class p(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(tag='p', single_line=True, **kwargs)

