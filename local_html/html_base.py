from utils import getparam


def htmlize(val):
    if isinstance(val, str):
        return '"{}"'.format(str(val))
    else:
        return '{}'.format(str(val))


class HtmlAttribute():
    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def format(self, cfg):
        key = self.key.replace('_hyphen_', '-')
        if key == 'clasz' or key == 'clazz':
            key = 'class'
        cfg.write(' {}'.format(key))
        if self.value is not None:
            cfg.write('={}'.format(htmlize(self.value)))


class HtmlElement():
    def __init__(self, **kwargs):
        self.children = []
        self.attrs = []
        self.tag = getparam(kwargs, 'tag', None, True)
        self.single_line = getparam(kwargs, 'single_line', False, True)
        self.close_tag = getparam(kwargs, 'close_tag', True, True)
        for key, value in kwargs.items():
            self.attr(HtmlAttribute(key, value))

    def attr(self, attr):
        self.attrs.append(attr)

    def child(self, elem):
        self.children.append(elem)
        return elem

    def has(self, elems):
        if isinstance(elems, list):
            for elem in elems:
                if elem is not None:
                    self.child(elem)
        else:
            self.child(elems)
        return self

    def format_attrs(self, cfg):
        for attr in self.attrs:
            attr.format(cfg)

    def format_open(self, cfg):
        cfg.startline('<{}'.format(self.tag))
        self.format_attrs(cfg)
        cfg.write('>')
        if not self.single_line:
            cfg.endline()

    def format_close(self, cfg):
        if self.close_tag:
            if not self.single_line:
                cfg.startline()
            cfg.write('</{}>'.format(self.tag))
        cfg.endline()

    def format_children(self, cfg):
        for child in self.children:
            if isinstance(child, HtmlElement):
                child.format(cfg)
            else:
                if not self.single_line:
                    cfg.startline()
                cfg.write(str(child))
                if not self.single_line:
                    cfg.endline()

    def format(self, cfg):
        self.format_open(cfg)
        if not self.single_line:
            cfg.inc()
        self.format_children(cfg)
        if not self.single_line:
            cfg.dec()
        self.format_close(cfg)

