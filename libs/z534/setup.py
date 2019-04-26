from setuptools import setup

setup(name='z534',
      version='0.1.1',
      description='Code for in-class project in Z534 at Indiana Univeristy',
      url='https://github.com/bsobolik/Z534',
      author='Dakota Murray',
      author_email='dakota.s.murray@gmail.com',
      license='MIT',
      packages=['z534'],
      install_requires=[
          'pymongo'
      ],
      zip_safe=False)
