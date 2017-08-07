# Instance Count
Uses boto3 to calculate the difference between Reserved Instances in AWS and
running EC2 Instances.

To run, just type:
```bash
$ ./instance_count.py
```

# Dependencies
Requires boto3 and colorama

```bash
$ pip install -U boto3 colorama
```
# AWS Creds
Uses standard Boto3 credential sources.  So, make sure your AWS ID and Secret
are made properly available.

# Running
You can output as terio or html via the `-p` flag.
You can output to stdout or to a file via the `-f` flag.

## Run with defaults, termio to stdout
![sample termio output][doc/images/termio_sample.png]

## Run with `-p html`
Note: because instance_count defaults to writing to stdout, the `-f index.html`
below is optional, and added for convenience.

```bash
$ ./instance_count.py -p html -f index.html
$
```

![sample html output][doc/images/html_sample.png]