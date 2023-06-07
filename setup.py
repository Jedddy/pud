import os
import sys
from setuptools import setup


with open("README.md", "r") as readme, \
    open("requirements.txt") as reqs:

    readme = readme.read()
    requirements = reqs.read().split("\n")


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


setup(
    name="pod",
    description="A command-line tool for navigating directories.",
    version="0.1.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Jedddy/pod",
    author="Jedddy",
    packages=["pod"],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pod = pod.main:main',
        ]
    }
)