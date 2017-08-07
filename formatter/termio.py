from colorama import init, Fore, Style
from formatter.formatter import Formatter


class TermioFormatter(Formatter):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.lines = []
        self.down_arrow = '\u2193'
        self.up_arrow = '\u2191'
        self.hline = '\u2500'
        init()

    def _format_expiry_period(self, expiries, period):
        if expiries.totals.get(period) == 0:
            return []

        lines = []
        pre_days = 'in the next '
        banner_days = ''
        multi = ' days'

        if period == 'month':
            banner_days = '30'
        elif period == 'week':
            banner_days = '7'
        else:
            pre_days = ''
            banner_days = 'today'
            multi = ''

        banner = 'The following will expire {}{}{}{}{}'.format(pre_days, Style.BRIGHT, banner_days, Style.RESET_ALL, multi)
        total = 0
        lines.append('\n{}'.format(banner))
        lines.append('{}{:<15s}{:>10}{}'.format(Style.BRIGHT, 'Type', 'Number', Style.RESET_ALL))
        lines.append('\u2500' * 25)
        for key, value in expiries.expiries.items():
            val = value.get(period)
            if val > 0:
                total += val
                lines.append('{:<15}{:>10}'.format(key, str(val)))
        lines.append('\u2500' * 25)
        lines.append('{}{:<15}{:>10}{}'.format(Style.BRIGHT, 'Total', str(total), Style.RESET_ALL))
        return lines

    def format_expiries(self, expiries):
        if len(expiries.expiries.keys()) == 0:
            self.lines.append("No instances expire in the next 30 days")
            return

        self.lines.extend(self._format_expiry_period(expiries, 'month'))
        self.lines.extend(self._format_expiry_period(expiries, 'week'))
        self.lines.extend(self._format_expiry_period(expiries, 'day'))

    def format_title(self, title):
        self.lines.extend([
            self.hline * 46,
            '{:^46}'.format(title),
            self.hline * 46
        ])

    def format_header(self):
        arrows = Fore.RED + self.up_arrow + Fore.WHITE + '/' + Fore.BLUE + self.down_arrow
        self.lines.extend([
            '{}{:<15s}{:>10}{:>10}{:>8}{}{}'.format(Style.BRIGHT, 'Type', 'Reserved', 'In Use', ' ', arrows, Style.RESET_ALL),
            self.hline * 46
        ])

    def format_total(self, reserved, in_use):
        self.lines.extend([
            self.hline * 46,
            self.format_line('Total', reserved, in_use, True)
        ])

    def format_line(self, key, reserved, in_use, is_total=False):
        style = Style.NORMAL
        diff = int(reserved - in_use)

        if is_total:
            style = Style.BRIGHT

        if diff > 0:
            # We have too many instances
            arrow = self.up_arrow
            color = Fore.RED
        elif diff < 0:
            arrow = self.down_arrow
            color = Fore.BLUE
        else:
            color = Fore.WHITE
            arrow = ''

        return '{}{:<15s}{:>10s}{:>10s}{}{:>10s}{}{}'.format(style, key, str(reserved), str(in_use), color, str(diff), arrow, Style.RESET_ALL)

    def format_deltas(self, r_instances, instances):
        r_total = 0
        iu_total = 0

        # For each instance type...
        for key, in_use in instances.types.items():
            reserved = r_instances.get(key)
            iu_total += in_use
            r_total += reserved
            self.lines.append(self.format_line(key, reserved, in_use))

        # Get any reserved instances types that don't have
        for key, reserved in r_instances.types.items():
            if key not in instances.types:
                r_total += reserved
                self.lines.append(self.format_line(key, reserved, 0))

        # Add the total lines
        self.format_total(r_total, iu_total)


    def format_table(self, title, instances, r_instances):
        self.format_title(title)
        self.format_header()
        self.format_deltas(r_instances, instances)
        self.format_expiries(r_instances.expiries)


    def format(self):
        for line in self.lines:
            self.cfg.writeline(line)
