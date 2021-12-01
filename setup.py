import os

from setuptools import setup, find_packages
import py2exe

main_dir = os.path.dirname(os.path.abspath(__file__))

setup_info = dict(
    name='limiter',
    version='1.0',
    author='Roi Halamish',
    author_email='roihalamish@gmail.com',
    description='Extending tws functionality',
    console=['main.py'],
    data_files=[('config', [os.path.join(main_dir, 'config', 'config.json')])],
    options={
        "py2exe": {}}
)

setup(**setup_info)
