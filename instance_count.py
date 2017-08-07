#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
import argparse
import boto3
from formatter.formatter import FormatConfig
from formatter.termio import TermioFormatter
from formatter.html import HtmlFormatter


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


def collect_ec2_info():
    client = boto3.client('ec2')
    instances = Instances(client)
    r_instances = ReservedInstances(client)
    return (instances, r_instances)


def collect_rds_info():
    client = boto3.client('rds')
    instances = RdsInstances(client)
    r_instances = ReservedRdsInstances(client)
    return (instances, r_instances)


def main():
    formatter = None
    parser = argparse.ArgumentParser(description='Calculate AWS instance diffs')
    parser.add_argument("-p", "--protocol", default="termio", help='The output protocol to use', choices=['html', 'termio'])
    parser.add_argument("-f", "--file", help='Optional file to output to. Defaults to stdout')
    args, unknownargs = parser.parse_known_args()
    protocol = args.protocol

    f = None
    if args.file:
        f = open(args.file, 'w')

    cfg = FormatConfig(f)

    if protocol == 'html':
        formatter = HtmlFormatter(cfg)
    else:
        formatter = TermioFormatter(cfg)

    instances, r_instances = collect_ec2_info()
    formatter.format_table('EC2 Instances', instances, r_instances)

    instances, r_instances = collect_rds_info()
    formatter.format_table('RDS Instances', instances, r_instances)

    formatter.format()


if __name__ == '__main__':
    main()