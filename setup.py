#!/usr/bin/env python
from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2',
]

install_requires = [
    'nodeconductor>0.148.3',
    'apache-libcloud>=1.1.0,<2.2.0',
    'cryptography',
]

setup(
    name='waldur-azure',
    version='0.3.3',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='https://waldur.com',
    description='Waldur plugin for managing MS Azure resources.',
    long_description=open('README.rst').read(),
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'nodeconductor_extensions': (
            'waldur_azure = waldur_azure.extension:AzureExtension',
        ),
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
