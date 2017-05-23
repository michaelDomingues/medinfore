#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='Medinfore',
      version='1.1.0',
      description='Indexing and searching engine in a medical corpus',
      author='Michael Domingues',
      author_email='dominguesjust@gmail.com',
      license='MIT',
      keywords='ehr api indexing',
      classifiers=[
          'Development Status :: 1 - Prototype',
          'Environment :: Console & Web',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Information Retrieval',
      ],
      packages=['api', 'documenthandler', 'languagemodel', 'redisdb', 'utilities'],
      install_requires=['flask', 'nltk', 'numpy', 'gensim', 'pprint', 'redis', 'PyMedTermino']
      )
