from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tpicview',
    version='1.0.0',
    description='View images and play gifs in the terminal',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['Pillow>=5.2.0'],

    entry_points={
        'console_scripts': [
            'tpicview=tpicview.tpicview:main'
        ],
    },
)
