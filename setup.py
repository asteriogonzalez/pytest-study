#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pytest-study',
    license='MIT',
    # packages=['pytest-study'],
    version='0.12',
    description="A pytest plugin to organize long run tests (named studies) without interfering the regular tests",
    author='Asterio Gonzalez',
    author_email='asterio.gonzalez@gmail.com',
    url='https://github.com/asteriogonzalez/pytest-study',
    # download_url = 'https://github.com/asteriogonzalez/pytest-study/archive/0.1.tar.gz',
    keywords = ['testing', 'pytest', 'studies', 'long_run'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],

    long_description=read("README.md"),
    py_modules=['pytest_study'],
    entry_points={'pytest11': ['study = pytest_study']},
    install_requires=['pytest>=2.0', 'blessings']
)
