"""The setup script """
from setuptools import setup, find_packages

setup(
    name='epm',
    version='0.0.1',
    description='EPM',
    long_description='EPM',
    url='https://github.com/NickeZ/epm',

    author='Niklas Claesson',
    author_email='nicke.claesson@gmail.com',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={
        'epm': ['resources/templates/*']
    },
    entry_points={
        'console_scripts': [
            'epm=epm:main',
        ],
    },
)
