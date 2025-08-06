import os
from setuptools import setup

reqs_path = os.path.join('coupled_modelling/', 'requirements.txt')
with open(reqs_path) as f:
    reqs = f.read().splitlines()

setup(
    name = 'coupled_modelling',
    version = '1.0',
    author = 'Ildar baimuratov',
    author_email = 'baimuratov.i@gmail.com',
    description = 'Modeling coupled systems with OWL',
    url = 'https://github.com/ldrbmrtv/coupled_modelling',
    license = 'MIT',
    packages = ['coupled_modelling'],
    install_requires = reqs
)
