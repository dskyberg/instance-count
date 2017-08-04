#!/usr/bin/env python
from setuptools import setup

setup(name='instance-count',
      version='1.0',
      description='Show diff between AWS instances and reserved instances.',
      author='David Skyberg',
      author_email='davidskyberg@gmail.com',
      url='https://www.github.org/dskyberg/instance-count/',
      nstall_requires=[
          'boto3>=1.4.5',
          'colorama>=0.3.9'
          ]
     )
