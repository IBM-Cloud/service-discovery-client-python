"""
A Python client for the Bluemix Service Discovery service

See:
https://github.com/IBM-Bluemix/service-discovery-client-python
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bluemix-service-discovery',
    version='0.0.1',
    description='Python client for the Bluemix Service Discovery service',
    long_description=long_description,
    url='https://github.com/IBM-Bluemix/service-discovery-client-python',
    author='Jake Peyser',
    author_email='jepeyser@us.ibm.com',
    license='Apache-2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3'
    ],
    keywords='service-discovery service-registry microservices',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests>=2'],
)
