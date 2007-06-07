import unittest

from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite
from zope.component import testing
from Testing import ZopeTestCase as ztc
from collective.testing.layer import ZCMLLayer

# these are used by setup
import transaction
import persistent
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection
from ZODB.tests.util import DB

from zope import component
import zope.component.interfaces
import zope.app.location.interfaces
from zope.app.testing import placelesssetup
from zope.app.keyreference.persistent import (
    KeyReferenceToPersistent, connectionOfPersistent)
from zope.app.component import site
from zope.app.folder import rootFolder
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
import zope.app.component.hooks
import zope.app.component.interfaces

from five.intid.site import add_intids
from OFS.SimpleItem import SimpleItem

class Demo(SimpleItem):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

def contentSetUp(app):
    for i in range(30):
        id = 'ob%d' % i
        app._setObject(id, Demo(id))

def ChinatownSetUp(app):
    characters = ['jake', 'evelyn', 'noah', 'hollis', 'katherine',
                  'the past', 'investigation']
    for c in characters:
        app._setObject(c, Demo(c))

def setUp(test):
    # Make a site, turn on the local site hooks, add the five.intid utility
    from collective.testing.utils import monkeyAppAsSite
    monkeyAppAsSite()
    from five.intid.site import add_intids
    from zope.app.component.hooks import setSite, setHooks
    add_intids(test.app)
    contentSetUp(test.app)
    setSite(test.app)
    setHooks()

class FuncLayer(ZCMLLayer):
    @classmethod
    def setUp(cls):
        from Products.Five import zcml
        from plone import relations
        zcml.load_config('configure.zcml', relations)

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
def test_suite():
    # Zope 2 + Five Integration tests that use ZopeTestCase
    integration = ztc.FunctionalDocFileSuite('container.txt',
                                             optionflags=optionflags,
                                             package='plone.relations',
                                             setUp=setUp)
    readme = ztc.FunctionalDocFileSuite('README.txt',
                                        optionflags=optionflags,
                                        package='plone.relations',
                                        setUp=setUp)
    integration.layer = readme.layer = FuncLayer

    lazy = DocTestSuite('plone.relations.lazylist')

    return unittest.TestSuite((integration, readme, lazy))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
