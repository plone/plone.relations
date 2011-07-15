import doctest
from doctest import DocTestSuite
import unittest

from Testing.ZopeTestCase import placeless
from Testing import ZopeTestCase as ztc

# these are used by setup
from five.intid.site import add_intids
from five.intid.lsm import USE_LSM
from OFS.SimpleItem import SimpleItem

class Demo(SimpleItem):
    def __init__(self, obid):
        self.id = obid
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

def contentSetUp(app):
    for i in range(30):
        obid = 'ob%d' % i
        ob_object = Demo(obid)
        app._setObject(obid, ob_object)

def ChinatownSetUp(app):
    characters = ['jake', 'evelyn', 'noah', 'hollis', 'katherine',
                  'the past', 'investigation']
    for c in characters:
        app._setObject(c, Demo(c))

def setUp(app):
    # turn on all needed zcml
    placeless.setUp()
    import Products.Five
    from Zope2.App import zcml
    from plone import relations
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('configure.zcml', relations)
    # Make a site, turn on the local site hooks, add the five.intid utility
    from zope.site.hooks import setSite, setHooks
    if not USE_LSM:
        # monkey in our hooks
        from Products.Five.site.metaconfigure import classSiteHook
        from Products.Five.site.localsite import FiveSite
        from zope.interface import classImplements
        from zope.site.interfaces import IPossibleSite
        klass = app.__class__
        classSiteHook(klass, FiveSite)
        classImplements(klass, IPossibleSite)
    add_intids(app)
    setSite(app)
    setHooks()
    contentSetUp(app)

def tearDown():
    placeless.tearDown()

optionflags = doctest.ELLIPSIS
def test_suite():
    # Zope 2 + Five Integration tests that use ZopeTestCase
    integration = ztc.FunctionalDocFileSuite('container.txt',
                                             optionflags=optionflags,
                                             package='plone.relations')
    readme = ztc.FunctionalDocFileSuite('README.txt',
                                        optionflags=optionflags,
                                        package='plone.relations')


    lazy = DocTestSuite('plone.relations.lazylist')

    return unittest.TestSuite((lazy, integration, readme))
