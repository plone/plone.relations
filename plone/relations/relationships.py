from Acquisition import Explicit, aq_parent, aq_inner
import persistent
from zope import interface
from zope.component import adapts
from Acquisition import aq_parent
import zope.app.container.contained
from zc.relationship.shared import Relationship as RelationshipBase
from zc.relationship import interfaces as zc_interfaces
from plone.relations import interfaces


class Relationship(RelationshipBase):
    interface.implements(interfaces.IRelationship)
    _relation = None

    def __init__(self, sources, targets, relation=None):
        self._sources = tuple(sources)
        self._targets = tuple(targets)
        # use the adapter to set the relation type
        if relation is not None:
            interfaces.IComplexRelationship(self).relation = relation

    def __repr__(self):
        return '<Relationship %r from %r to %r>' % (
                                 interfaces.IComplexRelationship(self).relation,
                                 self.sources,
                                 self.targets)

    # a bit of a kludge because the Five version of intid needs this
    def getPhysicalPath(self):
        path = (str(self.__name__),)
        p = self.__parent__ or aq_parent(aq_inner(self))
        if p is not None:
            path = p.getPhysicalPath() + path
        return path

# A version of the class with acquisition added so that Zope 2 security
# checks may be performed.
class Z2Relationship(Relationship, Explicit):
    pass

class ComplexRelationshipAdapter(object):
    interface.implements(interfaces.IComplexRelationship)
    adapts(interfaces.IRelationship)
    def __init__(self, rel):
        self.rel = rel

    @apply
    def relation():
        def get(self):
            return getattr(self.rel, '_relation', None)
        def set(self, value):
            self.rel._relation = value
            if zc_interfaces.IBidirectionalRelationshipIndex.providedBy(
                self.rel.__parent__):
                self.rel.__parent__.reindex(self.rel)
        return property(get, set)
