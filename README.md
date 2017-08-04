# Instance Count
Uses boto3 to calculate the difference between Reserved Instances in AWS and
running EC2 Instances.

To run, just type:
# Dependencies
Requires boto3 and colorama

```bash
$ pip install -U boto3 colorama
```
# AWS Creds
Uses standard Boto3 credential sources.  So, make sure your AWS ID and Secret
are made properly available.

```bash
$ ./instance_count.py
──────────────────────────────────────────────
                EC2 Instances
──────────────────────────────────────────────
Type             Reserved    In Use        ↑/↓
──────────────────────────────────────────────
c4.large                4         0         4↑
t2.medium               7         3         4↑
t2.micro               23         9        14↑
t2.nano                35         8        27↑
m3.medium               8         2         6↑
t2.large                5         1         4↑
r3.large                8         0         8↑
t2.small               12         4         8↑
m3.large                2         0         2↑
──────────────────────────────────────────────
Total                 104        27        77↑

The following will expire in the next 7 days
Type               Number
─────────────────────────
t2.small                4
─────────────────────────
Total                   4

The following will expire today
Type               Number
─────────────────────────
t2.nano                10
t2.micro               18
t2.medium               2
─────────────────────────
Total                  30

──────────────────────────────────────────────
                RDS Instances
──────────────────────────────────────────────
Type             Reserved    In Use        ↑/↓
──────────────────────────────────────────────
db.t2.micro             3         1         2↑
──────────────────────────────────────────────
Total                   3         1         2↑

No reservations expiring in the next 30 days
```