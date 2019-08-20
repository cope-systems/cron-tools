#!/usr/bin/env python
import os
from setuptools import setup


def load(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            return f.read()
    except IOError:
        return ''


REQUIREMENTS = [l for l in load('requirements.txt').split('\n') if l.strip() and not l.strip().startswith('#')]
VERSION = '0.1.0'

setup(
    name='cron-tools',
    version=VERSION,
    url='https://github.com/cope-systems/cron-tools',
    description='Tools for enhancing cron jobs and similar activities.',
    long_description=load("README.md"),
    author='Robert Cope',
    author_email='robert@copesystems.com',
    license='apache',
    platforms='any',
    packages=["cron_tools"],
    scripts=['cron-tools-wrapper.py', 'cron-tools-janitor.py', 'cron-tools-webapp.py'],
    entry_points={
        'console_scripts': []
    },
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache License',
        'Topic :: System',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    include_package_data=True,
    keywords="cron"
)
