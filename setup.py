import os
import sys
from setuptools import setup, find_packages


with open("README.md", "r") as readme, \
    open("requirements.txt") as reqs:

    readme = readme.read()
    requirements = reqs.read().split("\n")


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


setup(
    name="pud",
    description="A command-line tool for navigating directories.",
    version="1.0.2",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Jedddy/pud",
    author="Jedddy",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pud = pud.main:main',
        ]
    }
)
