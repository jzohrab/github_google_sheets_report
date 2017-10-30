# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='GitHubRepoAnalyzer',
    version='0.1.0',
    description='Analyze GitHub repo.',
    long_description=readme,
    author='Jeff Zohrab',
    author_email='jzohrab@gmail.com',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

