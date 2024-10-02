from setuptools import setup, find_packages

setup(
    name="dropbox",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'pytest'
    ],
    include_package_data=True,
)