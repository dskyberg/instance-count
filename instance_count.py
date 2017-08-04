#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
import boto3
from colorama import init, Fore, Back, Style


def flatten(fat_list):
    '''
    Flattens lists of lists at any depth into a single list. The lists can contain
    any type of values.
    Example:
    >>> flatten(['a','b','c', ['1','2','3',['4','5'],'6','7'],'8','9'])
    ['a', 'b', 'c', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    '''
    flattened = []
    if fat_list is None:
        return flattened
    if not isinstance(fat_list, list):
        raise ValueError('flatten - parameter must be a list. Found {}'.format(type(fat_list)))
    for elem in fat_list:
        if isinstance(elem, list):
            flattened.extend(flatten(elem))
        else:
            flattened.append(elem)
    return flattened


class Expiry():
    '''
    Keeps running totals of expiry periods, and provides print support to
    display the results to stdout.
    '''

    def __init__(self, limit=30):
        if limit < 1:
            raise ValueError('Expiry - limit must be greater than 0')

        self.day = 0
        self.week = 0
        self.month = 0

    def add(self, period, value):
        '''
        Adds a value to an expiry period.
        The period can be either a name [day, week, month], or a numeric value.
        As an int, the period is the number of days from the current date.
        '''

        if (isinstance(period, str) and period == 'day') or (isinstance(period, int) and period < 2):
            self.day += value
        elif (isinstance(period, str) and period == 'week') or (isinstance(period, int) and period < 8):
            self.week += value
        elif (isinstance(period, str) and period == 'month') or (isinstance(period, int) and period < 31):
            self.month += value
        else:
            if isinstance(period, str):
                raise ValueError('Expiry.add - Unknown period: {}'.format(period))
            elif isinstance(period, int):
                raise ValueError('Expiry.add - Bad value for period. Must be between 0 and 30: {}'.format(str(period)))
            else:
                raise ValueError('Expiry.add - Bad type for period. Must string or int: {}'.format(type(period)))

    def get(self, period):
        '''
        Returns the value for a period.
        The period can be either a name [day, week, month], or a numeric value.
        As an int, the period is the number of days from the current date.
        '''
        if (isinstance(period, str) and period == 'day') or (isinstance(period, int) and period < 2):
            return self.day
        elif (isinstance(period, str) and period == 'week') or (isinstance(period, int) and period < 8):
            return self.week
        elif (isinstance(period, str) and period == 'month') or (isinstance(period, int) and period < 31):
            return self.month
        else:
            if isinstance(period, str):
                raise ValueError('Expiry.get - Unknown period: {}'.format(period))
            elif isinstance(period, int):
                raise ValueError('Expiry.get - Bad value for period. Must be between 0 and 30: {}'.format(str(period)))
            else:
                raise ValueError('Expiry.get - Bad type for period. Must string or int: {}'.format(type(period)))


class ExpiryPeriods():
    '''
    Manages a dict of periods by keyword
    '''

    def __init__(self):
        now = datetime.utcnow()
        self.now = now.replace(tzinfo=timezone.utc)
        self.expiries = {}
        self.totals = Expiry()

    def _days(self, the_date):
        '''
        Private method.
        If the_date is after self.now, the days from self.now is returned.
        If the date is prior to self.now, _days returns a negative value.
        If the date is the same day as now, 0 is returned
        '''
        dtd = the_date - self.now
        return dtd.days

    def add(self, key, count, end_date):
        '''
        Increments the count by period for the associated key.
        '''

        days = self._days(end_date)
        if days > 30:
            return

        # Keep a running total  by period
        self.totals.add(days, count)

        if key in self.expiries:
            val = self.expiries[key]
        else:
            val = Expiry()

        val.add(days, count)
        self.expiries[key] = val

    def _show_period(self, period, raw):
        if self.totals.get(period) == 0:
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
        if raw:
            lines.append('\n"{}"'.format(banner))
            for key, value in self.expiries.items():
                if value > 0:
                    total += value[period]
                    lines.append('"{}"\t{}'.format(key, value[perios]))
            lines.append('"{}"\t{}'.format('Total', total))
        else:
            lines.append('\n{}'.format(banner))
            lines.append('{}{:<15s}{:>10}{}'.format(Style.BRIGHT, 'Type', 'Number', Style.RESET_ALL))
            lines.append('\u2500' * 25)
            for key, value in self.expiries.items():
                val = value.get(period)
                if val > 0:
                    total += val
                    lines.append('{:<15}{:>10}'.format(key, str(val)))
            lines.append('\u2500' * 25)
            lines.append('{}{:<15}{:>10}{}'.format(Style.BRIGHT, 'Total', str(total), Style.RESET_ALL))
        return lines

    def show(self, raw=False):
        lines = []
        if len(self.expiries.keys()) == 0:
            lines.append("No instances expire in the next 30 days")
            return
        lines.extend(self._show_period('month', raw))
        lines.extend(self._show_period('week', raw))
        lines.extend(self._show_period('day', raw))
        return '\n'.join(lines)


class InstancesBase():
    def __init__(self, client):
        self.client = client
        self.types = {}
        self.total = 0

    def get(self, key):
        if key in self.types:
            return self.types[key]
        return 0

    def add(self, key, value=1):
        self.total += value
        if key in self.types:
            val = self.types[key]
            self.types[key] = val + value
        else:
            self.types[key] = value

    def __str__(self):
        result = ''
        for k, v in self.types.items():
            result += '"{!s}"\t{!s}\n'.format(k, v)
        result += '{:<10}\t{}\n'.format('Total', self.total)
        return result


class Instances(InstancesBase):
    def __init__(self, client):
        super().__init__(client)
        self.filters = [
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
        self._run()

    def _run(self):
        response = self.client.describe_instances(Filters=self.filters)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                it = instance['InstanceType']
                self.add(it)


class ReservedInstances(InstancesBase):
    def __init__(self, client):
        super().__init__(client)
        self.expiries = ExpiryPeriods()
        self.filters = [
            {
                'Name': 'state',
                'Values': ['active']
            }
        ]
        self._run()

    def _run(self):
        response = self.client.describe_reserved_instances(Filters=self.filters)
        for instance in response['ReservedInstances']:
            it = instance['InstanceType']
            cnt = instance['InstanceCount']
            end = instance['End']
            self.add(it, cnt)
            self.expiries.add(it, cnt, end)


class RdsInstances(InstancesBase):
    def __init__(self, client):
        super().__init__(client)
        self.filters = [
            {
                'Name': 'state',
                'Values': ['running']
            }
        ]
        self._run()

    def _run(self):
        response = self.client.describe_db_instances()
        for instance in response['DBInstances']:
            it = instance['DBInstanceClass']
            self.add(it)


class ReservedRdsInstances(InstancesBase):
    def __init__(self, client):
        super().__init__(client)
        self.expiries = ExpiryPeriods()
        self.filters = [
            {
                'Name': 'state',
                'Values': ['active']
            }
        ]
        self._run()

    def _run(self):
        response = self.client.describe_reserved_db_instances()
        for instance in response['ReservedDBInstances']:
            it = instance['DBInstanceClass']
            cnt = instance['DBInstanceCount']
            startTime = instance['StartTime']
            duration = instance['Duration']
            end = startTime + timedelta(seconds=duration)
            self.add(it, cnt)
            self.expiries.add(it, cnt, end)


down_arrow = '\u2193'
up_arrow = '\u2191'
smiley = '\u263a'


def ansi_width(width, str, formatted_str):
    str_len = len(str)
    f_str_len = len(formatted_str)
    diff = f_str_len - str_len
    result = ' ' * diff
    result += formatted_str
    return result


def red(txt):
    return '{}{}{}'.format(Fore.RED, txt, Fore.RESET)


def blue(txt):
    return '{}{}{}'.format(Fore.BLUE, txt, Fore.RESET)


def white(txt):
    return '{}{}{}'.format(Fore.WHITE, txt, Fore.RESET)


def merge_line(key, cnt, in_use, diff, raw, style=Style.NORMAL):
    if diff > 0:
        # We have too many instances
        arrow = up_arrow
        color = Fore.RED
    elif diff < 0:
        arrow = down_arrow
        color = Fore.BLUE
    else:
        color = Fore.WHITE
        diff = smiley
        arrow = ''
    if raw:
        return '"{}"\t{}\t{}\t{}'.format(key, str(cnt), str(in_use), str(diff))
    else:
        return '{}{:<15s}{:>10s}{:>10s}{}{:>10s}{}{}'.format(style, key, str(cnt), str(in_use), color, str(diff), arrow, Style.RESET_ALL)


def merge_instances(r_instances, instances, raw=False):
    lines = []
    r_total = 0
    iu_total = 0
    d_total = 0

    for key, cnt in r_instances.types.items():
        in_use = instances.get(key)
        diff = int(cnt - in_use)

        r_total += cnt
        iu_total += in_use
        d_total += diff

        lines.append(merge_line(key, cnt, in_use, diff, raw))
    lines.append('\u2500' * 46)
    lines.append(merge_line('Total', r_total, iu_total, d_total, raw, Style.BRIGHT))
    return '\n'.join(lines)


def print_header(top, raw=False):
    arrows = Fore.RED + up_arrow + Fore.WHITE + '/' + Fore.BLUE + down_arrow
    if raw:
        print('{}{:^46}{}'.format(Style.BRIGHT, top, Style.RESET_ALL))
        print('"{}"\t"{}"\t"{}"\t"{}"{}'.format('Type', 'Reserved', 'In Use', arrows, Fore.RESET))
    else:
        print('\u2500' * 46)
        print('{:^46}'.format(top))
        print('\u2500' * 46)
        print('{}{:<15s}{:>10}{:>10}{:>8}{}{}'.format(Style.BRIGHT, 'Type', 'Reserved', 'In Use', ' ', arrows, Style.RESET_ALL))
        print('\u2500' * 46)


def print_instance_info(top, instances, r_instances, raw):
    merged_output = merge_instances(r_instances, instances, raw)
    expiry_output = r_instances.expiries.show()
    print_header(top, raw)
    print(merged_output)
    if expiry_output is not None:
        print(expiry_output)
    else:
        print('\nNo reservations expiring in the next 30 days')


def collect_ec2_info(raw=False):
    client = boto3.client('ec2')
    instances = Instances(client)
    r_instances = ReservedInstances(client)
    print_instance_info('EC2 Instances', instances, r_instances, raw)


def collect_rds_info(raw=False):
    client = boto3.client('rds')
    instances = RdsInstances(client)
    r_instances = ReservedRdsInstances(client)
    print_instance_info('RDS Instances', instances, r_instances, raw)


def main():
    raw = False
    init()
    collect_ec2_info(raw)
    print('')
    collect_rds_info(raw)


if __name__ == '__main__':
    main()