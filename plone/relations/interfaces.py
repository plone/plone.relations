from zope import interface
from zc.relationship.interfaces import IRelationship
from zc.relationship.interfaces import IRelationshipContainer

_marker = []

class IComplexRelationship(IRelationship):
    """An asymmetric relationship using sources, a relationship
    type (predicate), and targets:
    e.g. (Alice and Bob) are (enemies) of (Eve and Mallory)"""

    relation = interface.Attribute(
        """uniode: the single relationship type of this relationship;
        usually contains the verb of the sentence.""")


class IContextAwareRelationship(IRelationship):
    """A specialized relationship which provides a limited context in which the
    relationship is defined (e.g. two people may have a specific relationship in
    the context of a particular project or department, but a different one in
    another)"""

    def getContext():
        """return a context for the relationship"""


class IStatefulRelationship(IRelationship):
    """A specialized relationship where the relation itself has a state that
    evolves over time.  In particular, one may want relationships where the
    subject initiates the relationship, but it must be approved by the object
    of the relationship.  Or a relationship like a friendship, which may
    evolve over time through different stages
    ('acquaintance', 'chum', 'friend', 'BFF!')"""

    state = interface.Attribute(
        """unicode: the current state of the relationship""")


class IComplexRelationshipContainer(IRelationshipContainer):
    """An IRelationshipContainer like the one from zc.relationship, but with
    a little more complex relationship modelling.  It also supports pluggable
    transitivity models in case the default relationship independent model
    is too simple."""

    def findTargets(source, relation=_marker, state=_marker, context=_marker,
                    maxDepth=1, minDepth=None, filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

    def findSources(target, relation=_marker, state=_marker, context=_marker,
                    maxDepth=1, minDepth=None, filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

    def isLinked(source=None, target=None, relation=_marker,
                 state=_marker, context=_marker, minDepth=None,
                 maxDepth=1, filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for
        efficient filtering on state, context, and relationship."""

    def findRelationships(source=None, target=None, relation=_marker,
                          state=_marker, context=_marker, maxDepth=1,
                          minDepth=None, filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

    def findTargetTokens(source, relation=_marker, state=_marker,
                         context=_marker, maxDepth=1, minDepth=None,
                         filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

    def findSourceTokens(source, relation=_marker, state=_marker,
                         context=_marker, maxDepth=1, minDepth=None,
                         filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

    def findRelationshipTokens(source, relation=_marker, state=_marker,
                               context=_marker, maxDepth=1, minDepth=None,
                               filter=None, transitivity=None):
        """See IBidirectionalRelationshipIndex: includes support for efficient
        filtering on state, context, and relationship.
        """

class IRelatableProxy(interface.Interface):
    """It's an interface that describes an object which is capable to partecipating in a relationship"""

class IRelatableUnProxy(interface.Interface):
    """This interface describes an object which is a real partecipating to a relationship"""
