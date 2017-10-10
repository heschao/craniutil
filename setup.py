import re
from distutils.core import setup

import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('craniutil/__init__.py', encoding='utf_8_sig').read()
).group(1)

setup(
    name='craniutil',
    version=__version__,
    packages=['craniutil','craniutil.dbtest'],
    description='Utilities for Cranient Flask Projects',
    author='Chao Chen',
    author_email='chao@cranient.com',
    url='https://github.com/heschao/craniutil',
    long_description=open('README.md').read(), requires=['sqlalchemy', 'testing.postgresql']
)
