"""
The command pip install -e . is used for installing a Python package in editable mode from the current directory.
-e: This flag stands for editable mode. When you install a package in editable mode, it creates a link between the current directory 
(where the package code resides) and your Python environment. This is especially helpful during development because it allows you to make changes 
to the source code without having to reinstall the package every time.

Examples
--------
>>> pip install -e .
"""

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="tap30-taxi-demands-kaggle",
    version="0.1.0",
    author="Poorya Yousefi",
    packages=find_packages(),
    install_requires=requirements,
)
