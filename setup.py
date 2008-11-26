from setuptools import setup, find_packages

version = '1.0rc1'

setup(name='plone.relations',
      version=version,
      description="Tools for defining and querying complex relationships between objects",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
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
          "zc.relationship>=1.0.2",
          "five.intid",
      ],
      )
