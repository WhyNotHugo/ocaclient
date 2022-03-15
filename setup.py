#!/usr/bin/env python

from setuptools import setup

setup(
    name="ocaclient",
    description="A very simple client for OCA's web services.",
    author="Hugo Osvaldo Barrera",
    author_email="hugo@barrera.io",
    url="https://github.com/WhyNotHugo/ocaclient",
    license="ISC",
    packages=["ocaclient"],
    install_requires=[
        "python-dateutil",
        "lxml",
        "zeep>=3.0.0",
    ],
    long_description=open("README.rst").read(),
    use_scm_version={
        "version_scheme": "post-release",
        "write_to": "ocaclient/version.py",
    },
    setup_requires=["setuptools_scm"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
