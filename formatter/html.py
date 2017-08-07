from formatter.formatter import Formatter, FormatConfig
from local_html.elements import *


STYLES = [
    '.header-col{',
    '   border-bottom: 3px solid black;',
    '}',
    '.total-col{',
    '   border-top: 3px solid black;',
    '}',
    '.key-col{',
    '   font-weight: 600;',
    '}',
    '.arrow-col{',
    '   font-size: 1rem;',
    '}'
]


class HtmlFormatter(Formatter):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.down_arrow = '<i class="material-icons blue-text" style="font-size:22px;">arrow_downward</i>'
        self.up_arrow = '<i class="material-icons md-15 red-text" style="font-size:22px;">arrow_upward</i>'

        self.hline = '<i class="material-icons">face</i>'

        self.container = div(clazz='container')

        self.html = html().has([
            head().has([
                meta(charset='utf-8'),
                meta(name='viewport', content='width=device-width', initial_hyphen_scale=1),
                title('Instance Count'),
                link(href='https://fonts.googleapis.com/icon?family=Material+Icons', rel='stylesheet'),
                link(href='https://fonts.googleapis.com/css?family=Roboto', rel='stylesheet'),
                comment('Compiled and minified CSS'),
                link(href='https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.1/css/materialize.min.css', rel='stylesheet'),
                style(styles=STYLES)
            ]),
            body().has([
                self.container
            ])
        ])

    def _format_expiry_period(self, expiries, period):
        classes = 'col s2 l1 right-align '
        if expiries.totals.get(period) == 0:
            return

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

        total = 0

        self.container.has([
            div().has([
                span().has('The following will expire '), span().has(pre_days), span(style='font-weight:600;').has(banner_days), span().has(multi)
            ])
        ])

        self.container.has([
            div(clazz="row").has([
                div(clazz='col s2 l1 left-align key-col header-col', single_line=True).has('Type'),
                div(clazz=classes + ' header-col', single_line=True).has('Number')
            ])
        ])

        for key, value in expiries.expiries.items():
            val = value.get(period)
            if val > 0:
                total += val
                self.container.has([
                    div(clazz="row").has([
                        div(clazz='col s2 l1 left-align key-col ', single_line=True).has(key),
                        div(clazz=classes, single_line=True).has(val)
                    ])
                ])
        self.container.has([
            div(clazz="row").has([
                div(clazz='col s2 l1 left-align key-col total-col', single_line=True).has('Total'),
                div(clazz=classes + ' total-col', single_line=True).has(total)
            ])
        ])

    def format_expiries(self, expiries):
        if len(expiries.expiries.keys()) == 0:
            self.container.has([
                div().has(span().has('No instances expire in the next 30 days'))
            ])
            return

        self._format_expiry_period(expiries, 'month')
        self._format_expiry_period(expiries, 'week')
        self._format_expiry_period(expiries, 'day')

    def format_row(self, col1, col2, col3, col4, col_classes=''):
        classes = 'col s2 l1 right-align ' + col_classes
        i_class = 'material-icons'
        i_style = 'font-size:15px;'
        icon = 'arrow_upward'
        col4_classes = classes
        col5 = None
        if isinstance(col4, int):
            if col4 > 0:
                col4_classes += ' red-text'
                i_class += ' red-text'
                icon = 'arrow_upward'
            elif col4 < 0:
                col4_classes += ' blue-text'
                i_class += ' blue-text'
                icon = 'arrow_downward'
            col5 = div(clazz='col s1 m2 r1 left-align', single_line=True, style='padding-left:0 !Important;').has(i(icon, clazz=i_class, style=i_style))

        self.container.has([
            div(clazz='row').has([
                div(clazz='col s2 l1 left-align key-col ' + col_classes, single_line=True).has(col1),
                div(clazz=classes, single_line=True).has(col2),
                div(clazz=classes, single_line=True).has(col3),
                div(clazz=col4_classes, single_line=True, style='padding-right:0 !Important;').has(col4),
                col5
            ])
        ])

    def format_deltas(self, r_instances, instances):
        r_total = 0
        iu_total = 0

        # For each instance type...
        for key, in_use in instances.types.items():
            reserved = r_instances.get(key)
            iu_total += in_use
            r_total += reserved
            self.format_row(key, reserved, in_use, reserved-in_use)

        # Get any reserved instances types that don't have
        for key, reserved in r_instances.types.items():
            if key not in instances.types:
                r_total += reserved
                self.format_row(key, reserved, 0, reserved)

        # # Add the total lines
        self.format_row('Total', r_total, iu_total, r_total - iu_total, 'total-col')

    def format_title(self, table_title):
        self.container.has([
            div(clazz='row').has([
                div(clazz='col s8 l4 teal lighten-2 center-align', single_line=True).has([
                    table_title
                ])
            ])
        ])

    def format_header(self):
        arrows = '{}{}'.format(self.up_arrow, self.down_arrow)
        self.format_row('Type', 'Reserved', 'In Use', arrows, 'header-col')

    def format_table(self, table_title, instances, r_instances):
        self.format_title(table_title)
        self.format_header()
        self.format_deltas(r_instances, instances)
        self.format_expiries(r_instances.expiries)

    def format(self):
        self.html.format(self.cfg)

