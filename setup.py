import os
from setuptools import setup

setup(
        name = "zeitdownload",
        version = "1.0.1",
        author = "Christoph Stelz",
        author_email = "mail+python@ch-st.de",
        description = "Download the digital version of the newspaper \"Die Zeit\"",
        url = "https://github.com/stelzch/zeitdownloader",
        scripts = ['zeitdownload.py'],
        classifiers = [
            "Environment :: Console",
            "Topic :: Internet :: WWW/HTTP",
            "Intended Audience :: End Users/Desktop",
        ],
)
