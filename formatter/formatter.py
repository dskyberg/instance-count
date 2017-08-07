import sys


class FormatConfig():
    def __init__(self, file=None):
        if file is None:
            self.file = sys.stdout
        else:
            self.file = file
        self.indent = 0

    def inc(self):
        self.indent += 1
        return self.indent

    def dec(self):
        if self.indent > 0:
            self.indent -= 1
        return self.indent

    def istr(self):
        return '{}'.format('\t' * self.indent)

    def write(self, str):
        self.file.write(str)
        return self

    def startline(self, str=None, tab='\t'):
        self.write(tab * self.indent)
        if str is not None:
            self.write(str)
        return self

    def endline(self, str=None, end='\n'):
        if str is not None:
            self.write(str)
        self.write(end)

    def writeline(self, str, tab='\t', end='\n'):
        self.startline().write(str).endline()


class Formatter():
    def __init__(self, cfg):
        self.cfg = cfg

