from Acquisition import Explicit, aq_parent, aq_inner, aq_base
import persistent
from BTrees.IIBTree import IITreeSet
from zope import interface
from zope.component import adapts
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zc.relationship.shared import Relationship as RelationshipBase
from zc.relationship import interfaces as zc_interfaces
from plone.relations import interfaces

class IntIdSubObjectWrapper(IITreeSet):

    def __init__(self, initial):
        super(IntIdSubObjectWrapper, self).__init__(self._get_id(o) for o in
                                                                       initial)

    def _get_id(self, obj):
        resolver = getattr(self, '_v_intid_resolver', None)
        if resolver is None:
            resolver = self._v_intid_resolver = getUtility(IIntIds).getId
        return resolver(obj)

    def _get_object(self, intid):
        resolver = getattr(self, '_v_object_resolver', None)
        if resolver is None:
            resolver = self._v_object_resolver = getUtility(IIntIds).getObject
        return resolver(intid)

    def __iter__(self):
        for item in IITreeSet.__iter__(self):
            yield self._get_object(item)

    def __contains__(self, obj):
        return IITreeSet.__contains__(self, self._get_id(obj))

    def remove(self, obj):
        return IITreeSet.remove(self, self._get_id(obj))


class Relationship(RelationshipBase):
    interface.implements(interfaces.IRelationship)
    _relation = None

    def __init__(self, sources, targets, relation=None):
        self._sources = IntIdSubObjectWrapper(sources)
        self._targets = IntIdSubObjectWrapper(targets)
        # use the adapter to set the relation type
        if relation is not None:
            interfaces.IComplexRelationship(self).relation = relation
    @apply
    def sources():
        def get(self):
            return self._sources
        def set(self, value):
            self._sources = IntIdSubObjectWrapper(value)
            if zc_interfaces.IBidirectionalRelationshipIndex.providedBy(
                self.__parent__):
                self.__parent__.reindex(self)
        return property(get, set)

    @apply
    def targets():
        def get(self):
            return self._targets
        def set(self, value):
            self._targets = IntIdSubObjectWrapper(value)
            if zc_interfaces.IBidirectionalRelationshipIndex.providedBy(
                self.__parent__):
                self.__parent__.reindex(self)
        return property(get, set)

    def __repr__(self):
        return '<Relationship %r from %r to %r>' % (
                                 interfaces.IComplexRelationship(self).relation,
                                 tuple(self.sources),
                                 tuple(self.targets))

# A version of the class with acquisition added so that Zope 2 security
# checks may be performed.
class Z2Relationship(Relationship, Explicit):
    # a bit of a kludge because the Five version of intid needs this
    def getPhysicalPath(self):
        path = (str(self.__name__),)
        p = aq_parent(aq_inner(self)) or self.__parent__
        if p is not None:
            path = p.getPhysicalPath() + path
        return path

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
