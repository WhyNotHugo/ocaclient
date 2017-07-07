#!/usr/bin/env python

from setuptools import setup

setup(
    name='ocaclient',
    description="A very simple client for OCA's web services.",
    author='Hugo Osvaldo Barrera',
    author_email='hugo@barrera.io',
    url='https://gitlab.com/hobarrera/ocaclient',
    license='MIT',
    packages=['ocaclient'],
    install_requires=open('requirements.txt').readlines(),
    long_description=open('README.rst').read(),
    use_scm_version={
        'version_scheme': 'post-release',
        'write_to': 'ocaclient/version.py',
    },
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
