from setuptools import setup, find_packages

setup(
    name='fastApiSqlMap',
    version='0.1',
    packages=find_packages(where='src/third_lib'),
    package_dir={'': 'src/third_lib'},
    extras_require={
        'dev': ['flake8'],
    }
)