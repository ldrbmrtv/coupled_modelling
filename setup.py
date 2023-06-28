from setuptools import setup

with open('requirements.txt') as f:
    reqs = f.read().splitlines()

setup(
    name='coupled_modelling',
    version='1.0',
    author='Ildar baimuratov',
    author_email='baimuratov.i@gmail.com',
    description="Modelling coupled systems with OWL",
    url='https://github.com/ldrbmrtv/coupled_modelling',
    license='MIT',
    packages=['coupled_modelling'],
    install_requires=reqs,
    package_data={'coupled_modelling': ['*']},
)
