from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='teocomp',
    version='0.1.10',
    license='MIT',
    author="Davi Romero de Vasconcelos",
    author_email='daviromero@ufc.br',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/daviromero/teocomp',
    description='''TeoComp is a library for teaching Automata Theory, Languages and Theory of Computing.''',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='Theory of Computing, Automata Theory, Languages, Lambda-Calculus, Recursive Function (Kleene), Teaching Theory of Computing, Educational Software', 
    install_requires=[
        'graphviz',
        'pandas',
        'ipywidgets',
        'xmltodict', 
        'ruamel.yaml'
      ],

)
