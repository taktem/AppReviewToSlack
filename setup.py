# -*- coding: utf-8 -*-

from __future__ import with_statement
from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="appReviewToSlack",
    version="0.1.0",
    description="Post app review to slack",
    long_description="Post app review to slack",
    author="taktem",
    author_email="nishimura@taktem.com",
    url="https://github.com/taktem/AppReviewToSlack",
    py_modules=["appReviewToSlack"],
    include_package_data=True,
    install_requires=["requests"],
    tests_require=["nose"],
    license="MIT",
    keywords="",
    zip_safe=False,
    classifiers=[]
)
