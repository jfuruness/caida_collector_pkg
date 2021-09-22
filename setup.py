from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# https://stackoverflow.com/a/58534041/8903959
setup(
    name='lib_caida_collector',
    author="Justin Furuness, Matt Jaccino, Tony Zheng",
    author_email="jfuruness@gmail.com",
    version="0.0.2",
    url='https://github.com/jfuruness/lib_caida_collector.git',
    license="BSD",
    description="Downloads Caida AS-Serial relationships into a database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Furuness", "BGP", "Caida", "Relationships", "AS-Serial",
              "Peers", "Customers", "Providers"],
    include_package_data=True,
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        'lib_utils>=0.2.1',
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': 'lib_caida_collector = lib_caida_collector.__main__:main'},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
