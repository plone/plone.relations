import random
from Acquisition import Explicit, aq_base
from BTrees import OIBTree
import zope.container.btree
from zope.interface import implements
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zc.relationship import index
from zc.relationship.shared import ResolvingFilter
from zc.relationship.shared import minDepthFilter
from zc.relationship.shared import Container, AbstractContainer
from plone.relations import interfaces
from zc.relationship.index import generateToken, resolveToken
from plone.relations.interfaces import IRelatableProxy, IRelatableUnProxy

_marker = interfaces._marker

def dump(obj, index, cache):
    relatable = IRelatableProxy(obj, alternate=obj)
    return generateToken(relatable, index, cache)

def load(token, index, cache):
    obj = resolveToken(token, index, cache)
    related = IRelatableUnProxy(obj, alternate=obj)
    return related

def _update_query(query, relation, state, context):
    if relation != _marker:
        query['relation'] = relation
    if state != _marker:
        query['state'] = state
    if context != _marker:
        query['context'] = context

# A dumper, which is also a loader, for simple strings
def str_dump(obj, index, cache):
    return obj
str_load = str_dump

def _set_state(obj, dump, load, family):
    if dump is not None:
        obj['dump'] = dump
    if load is not None:
        obj['load'] = load
    if family is not None:
        obj['btree'] = family

# RelationshipContainers whose relationships need to interact with the
# security machinery of Zope 2 should inherit from one of the
# Acquisition base classes.
class RelationshipContainer(Container):

    # Set aatus so that we can retrieve entries, which are never protected.
    # The core methods are all protected via zcml declarations.
    # This is only necessary because of the use of restrictedTraverse in
    # five.intid's keyreference lookup. (see OFS.Folder)
    __allow_access_to_unprotected_subobjects__ = 1
    __name__ = 'relations'

    implements(interfaces.IComplexRelationshipContainer)
    def __init__(self,
                 dumpSource=dump, loadSource=load, sourceFamily=None,
                 dumpTarget=None, loadTarget=None, targetFamily=None,
                 dumpRelation=None, loadRelation=None, relationFamily=None,
                 dumpState=None, loadState=None, stateFamily=None,
                 dumpContext=None, loadContext=None, contextFamily=None,
                 **kwargs):
        # Override the AbstractContainer __init__
        source = {'element': interfaces.IRelationship['sources'],
                  'name': 'source', 'multiple': True}
        target = {'element': interfaces.IRelationship['targets'],
                  'name': 'target', 'multiple': True}
        relation = {'element': interfaces.IComplexRelationship['relation'],
                    'name': 'relation', 'dump': str_dump, 'load': str_load,
                    'btree': OIBTree}
        state = {'element': interfaces.IStatefulRelationship['state'],
                 'name': 'state', 'dump': str_dump, 'load': str_load,
                 'btree': OIBTree}
        context = {'element': interfaces.IContextAwareRelationship['getContext'],
                   'name': 'context'}

        # set all the non-string indices to use the source dump/load/storage if
        # specified
        if dumpSource is not None:
            target['dump'] = source['dump'] = context['dump'] = dumpSource
        if loadSource is not None:
            target['load'] = source['load'] = context['load'] = loadSource
        if sourceFamily is not None:
            target['btree'] = source['btree'] = context['btree'] = sourceFamily

        # set the more specific dump/load/family specs to their indices
        _set_state(target, dumpTarget, loadTarget, targetFamily)
        _set_state(relation, dumpRelation, loadRelation, relationFamily)
        _set_state(state, dumpState, loadState, stateFamily)
        _set_state(context, dumpContext, loadContext, contextFamily)

        ix = index.Index(
            (source, target, relation, state, context),
            index.TransposingTransitiveQueriesFactory('source', 'target'),
            **kwargs)
        self.relationIndex = ix
        ix.__parent__ = self
        zope.container.btree.BTreeContainer.__init__(self)

    def reindex(self, object):
        assert object.__parent__ is self
        self.relationIndex.index(object)

    def findTargets(self, source, relation=_marker, state=_marker,
                    context=_marker, maxDepth=1, minDepth=None, filter=None,
                    transitivity=None):
        query = {'source': source}
        _update_query(query, relation, state, context)
        return self.relationIndex.findValues(
            'target', self.relationIndex.tokenizeQuery(query),
            maxDepth, filter and ResolvingFilter(filter, self),
            targetFilter=minDepthFilter(minDepth),
            transitiveQueriesFactory=transitivity)

    def findSources(self, target, relation=_marker, state=_marker,
                    context=_marker, maxDepth=1, minDepth=None, filter=None,
                    transitivity=None):
        query = {'target': target}
        _update_query(query, relation, state, context)
        return self.relationIndex.findValues(
            'source', self.relationIndex.tokenizeQuery(query),
            maxDepth, filter and ResolvingFilter(filter, self),
            targetFilter=minDepthFilter(minDepth),
            transitiveQueriesFactory=transitivity)

    def findTargetTokens(self, source, relation=_marker, state=_marker,
                         context=_marker, maxDepth=1, minDepth=None,
                         filter=None, transitivity=None):
        query = {'source': source}
        _update_query(query, relation, state, context)
        return self.relationIndex.findValueTokens(
            'target', self.relationIndex.tokenizeQuery(query),
            maxDepth, filter and ResolvingFilter(filter, self),
            targetFilter=minDepthFilter(minDepth),
            transitiveQueriesFactory=transitivity)

    def findSourceTokens(self, target, relation=_marker, state=_marker,
                         context=_marker, maxDepth=1, minDepth=None,
                         filter=None, transitivity=None):
        query = {'target': target}
        _update_query(query, relation, state, context)
        return self.relationIndex.findValueTokens(
            'source', self.relationIndex.tokenizeQuery(query),
            maxDepth, filter and ResolvingFilter(filter, self),
            targetFilter=minDepthFilter(minDepth),
            transitiveQueriesFactory=transitivity)

    def isLinked(self, source=None, target=None, relation=_marker,
                 state=_marker, context=_marker, maxDepth=1, minDepth=None,
                 filter=None, transitivity=None):
        tokenize = self.relationIndex.tokenizeQuery
        query = {}
        _update_query(query, relation, state, context)
        if source is not None:
            query['source'] = source
            if target is not None:
                targetQuery = tokenize({'target': target})
            else:
                targetQuery = None
            return self.relationIndex.isLinked(
                tokenize(query),
                maxDepth, filter and ResolvingFilter(filter, self),
                targetQuery,
                targetFilter=minDepthFilter(minDepth),
                transitiveQueriesFactory=transitivity)
        elif target is not None:
            query['target'] = target
            return self.relationIndex.isLinked(
                tokenize(query),
                maxDepth, filter and ResolvingFilter(filter, self),
                targetFilter=minDepthFilter(minDepth),
                transitiveQueriesFactory=transitivity)
        else:
            raise ValueError(
                'at least one of `source` and `target` must be provided')

    def findRelationshipTokens(self, source=None, target=None, relation=_marker,
                               state=_marker, context=_marker, maxDepth=1,
                               minDepth=None, filter=None, transitivity=None):
        tokenize = self.relationIndex.tokenizeQuery
        query = {}
        _update_query(query, relation, state, context)
        if source is not None:
            query['source'] = source
            if target is not None:
                targetQuery = tokenize({'target': target})
            else:
                targetQuery = None
            res = self.relationIndex.findRelationshipTokenChains(
                tokenize(query),
                maxDepth, filter and ResolvingFilter(filter, self),
                targetQuery,
                targetFilter=minDepthFilter(minDepth),
                transitiveQueriesFactory=transitivity)
            return self._forward(res)
        elif target is not None:
            query['target'] = target
            res = self.relationIndex.findRelationshipTokenChains(
                tokenize(query),
                maxDepth, filter and ResolvingFilter(filter, self),
                targetFilter=minDepthFilter(minDepth),
                transitiveQueriesFactory=transitivity)
            return self._reverse(res)
        elif relation is not _marker or context is not _marker:
            res = self.relationIndex.findRelationshipTokenChains(
                tokenize(query),
                maxDepth, filter and ResolvingFilter(filter, self),
                targetFilter=minDepthFilter(minDepth),
                transitiveQueriesFactory=transitivity)
            return self._reverse(res)
        else:
            raise ValueError(
                'at least one of `source`, `target`, `relation`, or `context` '
                'must be provided')

    def findRelationships(self, source=None, target=None, relation=_marker,
                          state=_marker, context=_marker, maxDepth=1,
                          minDepth=None, filter=None, transitivity=None):
        return self._resolveRelationshipChains(
            self.findRelationshipTokens(
                source, target, relation, state, context, maxDepth,
                minDepth, filter, transitivity=transitivity))

    # We cannot use _ in names because it causes random-ish problems in Zope2
    def _generate_id(self, relationship):
        return ''.join(random.sample(
            "abcdefghijklmnopqrtstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890",
            30)) # somewhat less than 64 ** 30 variations (64*63*...*35)

# A version of the class with acquisition added so that Zope 2 security
# checks may be performed on the contained objects.  Note: when this container
# is acquisition wrapped, you will not be able to iterate over its keys using
# list(container) or the 'in' operator due to some odd acquisition behavior.
class Z2RelationshipContainer(RelationshipContainer, Explicit):

    def __init__(self, name=None, *args, **kw):
            self.__name__ = name
            super(Z2RelationshipContainer, self).__init__(*args, **kw)

    def manage_fixupOwnershipAfterAdd(self):
        pass

    def __getitem__(self, key):
        # acquisition wrap the output
        val = super(Z2RelationshipContainer, self).__getitem__(key)
        if hasattr(val, '__of__'):
            val = val.__of__(self)
        return val

    def get(self, key, default=None):
        # acquisition wrap the output
        val = super(Z2RelationshipContainer, self).get(key, default)
        if hasattr(val, '__of__'):
            val = val.__of__(self)
        return val

    def reindex(self, object):
        assert aq_base(object.__parent__) is aq_base(self)
        self.relationIndex.index(object)

    def remove(self, object):
        key = object.__name__
        if aq_base(self[key]) is not aq_base(object):
            raise ValueError("Relationship is not stored as its __name__")
        self.relationIndex.unindex(object)
        # we need to manually send the ObjectRemovedEvent, because acquisition
        # wrapping prevents it from firing automatically.
        notify(ObjectRemovedEvent(object, self, key))
        super(AbstractContainer, self).__delitem__(key)
