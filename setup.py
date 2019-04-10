import os
import inspect
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


def read_version(package):
    with open(os.path.join(package, '__init__.py'), 'r') as fd:
        for line in fd:
            if line.startswith('__version__ = '):
                return line.split()[-1].strip().strip("'")


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split('\\n') if req != '']


def read(fname):
    return open(os.path.join(__location__, fname)).read()


VERSION = read_version('n26')

setup(
    description='API and command line tools to interact with the https://n26.com/ API',
    long_description='API and command line tools to interact with the https://n26.com/ API',
    author='Felix Mueller',
    author_email='felix@s4ku.com',
    url='https://github.com/femueller/python-n26',
    download_url='https://github.com/femueller/python-n26/tarball/{version}'.format(version=VERSION),
    version=VERSION,
    install_requires=['requests', 'pyyaml', 'click', 'tabulate'],
    test_requires=['mock', 'pytest'],
    packages=[
        'n26'
    ],
    scripts=[],
    name='n26',
    entry_points={
        'console_scripts': ['n26 = n26.cli:cli']
    }
)
