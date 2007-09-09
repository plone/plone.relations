from setuptools import setup, find_packages

version = '0.1'

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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
