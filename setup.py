# coding=utf-8
from setuptools import setup

setup(
    name='etcdlock',
    package_dir = {'': 'src'},
    packages=['etcdlock'],
    version='1.0',
    description='A command line lock/mutex using etcd',
    author='Santtu Järvi',
    url='',
    entry_points={
        'console_scripts': [
            'etcdlock = etcdlock.etcdlock:main',
        ],
    },
    keywords=['etcd', 'lock', 'mutex'],
    install_requires=[
        'python-etcd',
    ],
    classifiers=["Programming Language :: Python :: 3"],
)