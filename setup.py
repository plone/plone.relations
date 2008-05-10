from setuptools import setup, find_packages

version = '1.0b5'

setup(name='plone.relations',
      version=version,
      description="Tools for defining and querying complex relationships between objects",
      long_description=open("plone/relations/README.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='references relationships plone',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://svn.plone.org/svn/plone/plone.relations',
      license='GPL with container.txt covered by ZPL and owned by Zope Corp.',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "zc.relationship>=1.0.2,<1.1dev",
          "five.intid",
      ],
      )
