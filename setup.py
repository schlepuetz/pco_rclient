#!/usr/bin/env python
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'Readme.md')).read()

setup(name='pco_rclient',
      version='0.3.0',
      description="Rest client script for the pco writer.",
      long_description=README,
      author='Paul Scherrer Institute (PSI)',
      maintainer="Paul Scherrer Institute",
      maintainer_email="daq@psi.ch",
      url='https://github.com/paulscherrerinstitute/pco_rclient',
      license="GPL3",
      packages=['pco_rclient'],
      )
