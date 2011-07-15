import os
from setuptools import setup, find_packages

version = '2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('plone', 'relations', 'README.txt')
    )

setup(name='plone.relations',
      version=version,
      description="Tools for defining and querying complex relationships between objects",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        ],
      keywords='references relationships plone',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://pypi.python.org/pypi/plone.relations',
      license='GPL with container.txt covered by ZPL and owned by Zope Corp.',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "zc.relationship>=1.1.1",
          "five.intid",
          "zope.container",
          "zope.intid",
          "zope.lifecycleevent",
          "zope.site",
          "Zope2 >= 2.13",
      ],
      )
