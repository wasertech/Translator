#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import translator

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


setup(
    name='interpres',
    author='Danny Waser',
    version=translator.__version__,
    license='LICENSE',
    url='https://github.com/wasertech/Translator',
    description='Translate from one language to another.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages('.'),
    python_requires='>=3.8,<3.11',
    install_requires = [
        'transformers~=4.25.1',
        'langcodes~=3.3.0',
        'datasets~=2.10.1',
        'halo~=0.0.31',
        'psutil~=5.9.4',
        'shutils~=0.1.0',
        'accelerate~=0.17.0',
        'questionary~=1.10.0',
    ],
    entry_points={
        'console_scripts': [
            'translate = translator.main:main',
        ]
    },
)
