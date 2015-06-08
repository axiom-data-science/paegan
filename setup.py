from __future__ import with_statement

from setuptools import setup, find_packages

from paegan import __version__


def readme():
    with open('README.md') as f:
        return f.read()

reqs = [line.strip() for line in open('requirements.txt')]

setup(
    namespace_packages = ['paegan'],
    name                 = "paegan",
    version              = __version__,
    description          = "Processing and Analysis for Numerical Data",
    long_description     = readme(),
    license              = 'GPLv3',
    author               = "Kyle Wilcox",
    author_email         = "kyle@axiomdatascience.com",
    url                  = "https://github.com/axiom-data-science/paegan",
    packages             = find_packages(),
    install_requires     = reqs,
    classifiers          = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
        ],
    include_package_data = True,
) 
