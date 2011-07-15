Detailed Documentation
======================

Overview
--------

This is a product built on the ``zc.relationship`` product for Zope 3.
It attempts to allow the functionality of that package to be used from
Zope 2, along with some simple additional functionality derived from
that package's basic relationship ``Index``.

The relationship container provided here is very similar to the one in
``zc.relationship``.  It is used to store and query objects
implementing or adaptable to the simple IRelationship interface, but
more complex relationships are supported as well.  This extra
functionality is defined in a few extensions to the IRelationship
interface.  These interfaces are described below:

    IRelationship defines a basic relationship consisting of
    only ``sources`` and ``targets``.  These are sequences of
    objects that comprise the relationship.  In the default
    implementation these must all be persistent objects from
    the ZODB (or more generally, objects for which and
    ``intid`` can be generated using the available ``IIntId``
    utility (cf ``zope.intid`` and ``five.intid``)).

    IComplexRelationship adds a relationship predicate to
    indicate the type of relationship involved.  This
    predicate is retrieved from an attribute called
    ``relation`` which should be an immutable unicode string
    (so a zope.i18n.Message can be used) in the default
    implementation.

    IContextAwareRelationship adds a context in which the
    relationship applies.  This context is provided by a
    method called ``getContext`` which, in the default
    implementation, should return objects of the same sort
    required by IRelationship (e.g. persistent objects from
    the ZODB).  An example: a hierarchical relationship which
    exists only within the _context_ of a specific department
    or project.

    IStatefulRelationship adds a relationship state to
    indicate the status of a particular relationship in the
    case that the relationship is one which changes over time
    or as a result of user actions.  This state is retrieved
    from an attribute called ``state`` which should be an
    immutable unicode string (see above). For example: a
    relationship which requires explicit approval by the
    involved target objects, it would start in an unapproved
    ``state`` and then transition to approved when the target
    objects had signaled their approval.  Also, the ``state``
    may represent a different stages of a particular
    relationship, e.g. ``stranger``, ``acquaintance``,
    ``pal``, ``friend``, ``BFF``.


These additional interfaces are entirely optional and may will be
looked up using adaptation to the desired interface.  So the
relationship objects themselves do not have to directly provide these
properties or methods, though that is also possible.  Only ``sources``
and ``targets`` are required to make a query-able relationship.

This additional richness could have been obtained using post query
filters, as supported by the default ``zc.relationship`` container.
However, filtering in this way is much less efficient that allowing
these potentially common attributes to be indexed and queried directly
(especially when doing so only results in a small increase in storage
requirements.


Using This Package
------------------

The basic functionality provided by this package is demonstrated and
tested in ``container.txt``, which essentially duplicates the
container tests from ``zc.relationship`` in a Zope 2 environment.
This section demonstrates some basic usage, as well as the features
provided by additional interfaces described above.

First you need a site with some content and by default an ``IIntId``
utility.  This was created for us by the test setup which has provided
us with an ``app`` an ``IIntId`` utility provided by the
``five.intid`` package.  Additionally, we need to create a
relationship container to use:

    >>> from plone.relations import tests
    >>> tests.setUp(app)

    >>> import transaction
    >>> from plone.relations import interfaces
    >>> from plone.relations.container import Z2RelationshipContainer
    >>> container = Z2RelationshipContainer()
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IComplexRelationshipContainer, container)
    True
    >>> app._setOb('references', container)
    >>> container.__name__ = 'references'
    >>> container.__parent__ = app
    >>> container = app['references']


This would generally be registered as a named local utility providing
the ``IComplexRelationshipContainer`` interface, but we will use it
directly.  Now we make some relationships, using the provided
``Relationship`` class which implements ``IRelationship`` and has a
built-in adapter to IComplexRelationship.  To properly illustrate the
potential complexity of relationships we will use some characters and
contexts from the 1974 film _Chinatown_:

    >>> from plone.relations.tests import ChinatownSetUp
    >>> ChinatownSetUp(app) #creates our characters and contexts
    >>> from plone.relations.relationships import Z2Relationship as Relationship
    >>> rel1 = Relationship((app['noah'],), (app['evelyn'],), relation='parent')
    >>> verifyObject(interfaces.IRelationship, rel1)
    True
    >>> interfaces.IComplexRelationship(rel1).relation
    'parent'
    >>> container.add(rel1)
    >>> rel2 = Relationship((app['hollis'],), (app['noah'],), relation='business-partner')
    >>> container.add(rel2)

Note that there is a default adatper for IRelationship objects which
provides IComplexRelationship using a simple attribute on the
relationship.

Then we add a relationship with a state, by directly applying the
interface and adding the attribute (which is not such a great way to
do this):

    >>> rel3 = Relationship((app['hollis'],), (app['evelyn'],), relation='intimate')
    >>> rel3.state = 'married'
    >>> from plone.relations.interfaces import IStatefulRelationship
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(rel3, IStatefulRelationship)
    >>> container.add(rel3)

We currently have a simple tree::

    noah <---(business-partner)---
     | (parent)                   |
     v                            |
   evelyn <-(intimate:married)- hollis

Now we can make queries against this simple data set, like finding
objects for which a another object is the source or target:

    >>> list(container.findTargets(source=app['hollis']))
    [<Demo noah>, <Demo evelyn>]
    >>> list(container.findTargets(source=app['hollis'], relation='intimate'))
    [<Demo evelyn>]
    >>> list(container.findTargets(source=app['hollis'], relation='intimate', state='married'))
    [<Demo evelyn>]
    >>> list(container.findTargets(source=app['hollis'], relation='intimate', state='divorced'))
    []
    >>> list(container.findTargets(source=app['evelyn'], relation='parent'))
    []
    >>> list(container.findTargets(source=app['noah'], relation='parent'))
    [<Demo evelyn>]
    >>> list(container.findSources(target=app['evelyn']))
    [<Demo noah>, <Demo hollis>]
    >>> list(container.findSources(target=app['evelyn'], relation='parent'))
    [<Demo noah>]
    >>> list(container.findSources(target=app['evelyn'], relation='intimate'))
    [<Demo hollis>]


Transitivity
------------

We can also generate a list of relationships, and even look
transitively at chains of relationships by specifying a maxDepth (and
optionally a minDepth) for any of the queries.  In particular the
findRelationships method will seek out chains of relationship matching
the specified parameters.  Let's look at the ways that ``hollis`` and
``evelyn`` are connected:

    >>> list(container.findRelationships(source=app['hollis'],
    ...                                  target=app['evelyn'], maxDepth=2))
    [(<Relationship 'intimate' from (<Demo hollis>,) to (<Demo evelyn>,)>,), (<Relationship 'business-partner' from (<Demo hollis>,) to (<Demo noah>,)>, <Relationship 'parent' from (<Demo noah>,) to (<Demo evelyn>,)>)]

``Hollis`` is ``evelyn's`` husband, and also her father's associate.


Modifying Relationships
-----------------------

The above method also allows us to access existing relationships
directly, which is especially helpful when we want to alter them.  In
this case ``hollis`` has been _murdered_; so ``evelyn`` is now his
widow. We express this with a state change on the relationship, note that
we have to reindex the relationship after applying the state directly
to it, if we had used an adapter to provide the state, then it should
have taken care of this for us when the attribute was set.:

    >>> relations = container.findRelationships(target=app['evelyn'], relation='intimate')
    >>> relations = list(relations)
    >>> relations
    [(<Relationship 'intimate' from (<Demo hollis>,) to (<Demo evelyn>,)>,)]
    >>> marriage = relations[0][0]
    >>> marriage.state = 'widowed'
    >>> container.reindex(marriage) # an adapter could handle this, as
    ...                             # we'll see later with context

We have changed the state of the marriage, let's ensure we can still
find it the same way we did before, but also using out new state:

    >>> list(container.findTargets(source=app['hollis'], relation='intimate'))
    [<Demo evelyn>]
    >>> list(container.findTargets(source=app['hollis'], relation='intimate', state='widowed'))
    [<Demo evelyn>]
    >>> list(container.findTargets(source=app['hollis'], relation='intimate', state='happy'))
    []

Now let's add some more relationships, including one with an unknown
``relation``. Here is the new relation tree::

            noah <----(business-partner)---
             | (parent)                    |
             v                             |
           evelyn <-(intimate:widowed)- hollis
             /\
    (client)/  \ (??)
           v    v
        jake    katherine

and the associated code:

    >>> rel4 = Relationship((app['evelyn'],), (app['jake'],), relation='client')
    >>> rel5 = Relationship((app['evelyn'],), (app['katherine'],))
    >>> container.add(rel4)
    >>> container.add(rel5)


    >>> sorted([repr(r) for r in container.findTargets(source=app['evelyn'])])
    ['<Demo jake>', '<Demo katherine>']
    >>> list(container.findTargets(source=app['evelyn'], relation=None))
    [<Demo katherine>]
    >>> list(container.findTargets(source=app['noah'], relation=None))
    []

Note that we can find entries with empty parameters using None as the
query argument.


Finding if Objects Are Related
-------------------------------

We can use maxDepth, like we did with the ``findRelationship``
queries, for any other query methods. A particularly useful one is
``isLinked``, which determines if any matching relationship chains
exist for a given query:

    >>> sorted([repr(r) for r in container.findTargets(source=app['noah'],
    ...                                                maxDepth=2)])
    ['<Demo evelyn>', '<Demo jake>', '<Demo katherine>']
    >>> container.isLinked(source=app['noah'], target=app['jake'])
    False
    >>> container.isLinked(source=app['noah'], target=app['jake'], maxDepth=2)
    True
    >>> container.isLinked(source=app['noah'], target=app['katherine'],
    ...                    relation='parent', maxDepth=2)
    False

So, as far as we know, ``noah`` and ``katherine`` are not linked via
parental relationships.


Context
--------

Now we'll apply a context to an existing relationship using a simple
adapter, in the real world this extra data would probably be stored
using an annotation on the relationship, but here we store it directly:

    >>> class ContextAdapter(object):
    ...     def __init__(self, relationship):
    ...         self.relationship = relationship
    ...     def getContext(self):
    ...         return getattr(self.relationship, '_context', None)
    ...     def setContext(self, context):
    ...         self.relationship._context = context
    ...         #reindex ourself in the container
    ...         if self.relationship.__parent__ is not None:
    ...             self.relationship.__parent__.reindex(self.relationship)
    >>> from zope.component import provideAdapter
    >>> provideAdapter(ContextAdapter, (interfaces.IRelationship,), interfaces.IContextAwareRelationship)

Right now the ``client`` relationship between ``evelyn`` and ``jake``
doesn't tell us much because there are potentially many different
contexts for a client relationship.  In this case ``jake`` is a
private investigator and the context is the ``investigation`` of
``hollis'`` murder.  This ``investigation`` object could consist of
notes pertaining to the investigation or other relevant data.  We
apply it to the relationship as a context:

    >>> list(container.findSources(target=app['jake'], relation='client',
    ...                            context=app['investigation']))
    []
    >>> relationships = list(container.findRelationships(source=app['evelyn'],
    ...                                                  target=app['jake']))
    >>> relationships
    [(<Relationship 'client' from (<Demo evelyn>,) to (<Demo jake>,)>,)]
    >>> evelyn_jake = relationships[0][0]
    >>> interfaces.IContextAwareRelationship(evelyn_jake).setContext(
    ...                                                   app['investigation'])
    >>> list(container.findSources(target=app['jake'], relation='client',
    ...                            context=app['investigation']))
    [<Demo evelyn>]
    >>> list(container.findSources(target=app['jake'], context=None))
    []
    >>> list(container.findSources(target=app['katherine'], context=None))
    [<Demo evelyn>]


In time some additional relationships develop. ``Jake`` and ``katherine``
have a fling during the investigation.  Also, ``jake`` becomes suspicious
of ``hollis'`` business partner and father-in-law ``noah``:

    >>> rel6 = Relationship((app['jake'],), (app['evelyn'],), 'intimate')
    >>> rel6.state = 'fling'
    >>> interfaces.IContextAwareRelationship(rel6).setContext(app['investigation'])
    >>> rel7 = Relationship((app['jake'],), (app['noah'],), 'nemesis')
    >>> interfaces.IContextAwareRelationship(rel7).setContext(app['investigation'])
    >>> container.add(rel6)
    >>> container.add(rel7)


Multiple Relationship Chains and Cycles
---------------------------------------

We've got a fairly complex graph, but an existing relationship becomes
a little clearer, when we learn katherine is evelyn's sister:

    >>> murky = list(container.findRelationships(source=app['evelyn'],
    ...                                          target=app['katherine']))
    >>> evelyn_katherine = murky[0][0]
    >>> interfaces.IComplexRelationship(evelyn_katherine).relation = 'sibling'

Here's the current relationship tree in ASCII form::

            (nemesis)---->noah <-----(business-partner)--
     [investigation]|      | (parent)                    |
                    |      v                             |
    (intimate:fling)|--> evelyn <-(intimate:widowed)- hollis
    [investigation] |      /\
                    |(client)\
               [investigation]\ (sibling)
                    |   /      \
                    |  v        v
                    jake       katherine

This complexity will allow us to explore how the relationship query
mechanisms resolve multiple relationship paths:

    >>> list(container.findTargets(source=app['jake'], context=app['investigation']))
    [<Demo evelyn>, <Demo noah>]
    >>> list(container.findRelationships(context=app['investigation']))
    [(<Relationship 'client' from (<Demo evelyn>,) to (<Demo jake>,)>,), (<Relationship 'intimate' from (<Demo jake>,) to (<Demo evelyn>,)>,), (<Relationship 'nemesis' from (<Demo jake>,) to (<Demo noah>,)>,)]

The first findTargets example above shows all the people that are
``jake's`` targets in the context of the investigation.  Then we have
a map of all the relationships that apply in the context of the
investigation.

In the end of the film we discover some rather sinister connections
between these characters.  ``Noah`` was ``hollis'`` murderer, and also
had an inappropriate intimate relationship with his daughter
``evelyn`` which resulted in their daughter ``katherine``.  We add
those relationships below (note how one can use multiple sources or
targets for a single relationship with ``noah`` and ``evelyn`` the
sources for their parental relationship with ``katherine``)::

    noah-(intimate[the past])->evelyn
       |\                     /
       | \                   /
       |  \                 /
       |   \  (parents)    /
       |    -->katherine<--
   (murderer)
       |
     hollis

and the code:

    >>> rel8 = Relationship((app['noah'],), (app['evelyn'],), 'intimate')
    >>> interfaces.IContextAwareRelationship(rel8).setContext(app['the past'])
    >>> container.add(rel8)

    >>> rel9 = Relationship((app['noah'],), (app['hollis'],), 'murderer')
    >>> container.add(rel9)

    >>> rel10 = Relationship((app['evelyn'], app['noah']), (app['katherine'],),
    ...                      'parent')
    >>> container.add(rel10)

At this point the relationship tree is far too complex and full of
loops to draw understandably using ascii art. However, it's no trouble
for our relationship container to inspect it:

    >>> list(container.findSources(target=app['katherine'], relation='parent', maxDepth=None))
    [<Demo evelyn>, <Demo noah>]
    >>> list(container.findRelationships(source=app['noah'],
    ...                                  target=app['katherine'],
    ...                                  relation='parent', maxDepth=None))
    [(<Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>,), (<Relationship 'parent' from (<Demo noah>,) to (<Demo evelyn>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)]

This is the same query we tried earlier when we were unclear of
relation between ``katherine`` and ``noah``.  Now we can see that
``noah`` is both her father and grandfather (ick!).

Exploring the relationships pointing to ``katherine`` from ``evelyn``
yields a pretty crazy picture, even when we restrict ourselves to
paths of at most 2 relationships (we need to play some tricks to
ensure that the results are returned in a repeatable order, so that
this test passes):

    >>> relations = container.findRelationships(target=app['katherine'],
    ...                                         maxDepth=2)
    >>> res = [repr(r) for r in relations]
    >>> res.sort(key=lambda x:(len(x), x)) # sort by length
    >>> print '\n'.join(res)
    (<Relationship 'sibling' from (<Demo evelyn>,) to (<Demo katherine>,)>,)
    (<Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>,)
    (<Relationship 'parent' from (<Demo noah>,) to (<Demo evelyn>,)>, <Relationship 'sibling' from (<Demo evelyn>,) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo jake>,) to (<Demo evelyn>,)>, <Relationship 'sibling' from (<Demo evelyn>,) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo noah>,) to (<Demo evelyn>,)>, <Relationship 'sibling' from (<Demo evelyn>,) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo hollis>,) to (<Demo evelyn>,)>, <Relationship 'sibling' from (<Demo evelyn>,) to (<Demo katherine>,)>)
    (<Relationship 'nemesis' from (<Demo jake>,) to (<Demo noah>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)
    (<Relationship 'parent' from (<Demo noah>,) to (<Demo evelyn>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo jake>,) to (<Demo evelyn>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo noah>,) to (<Demo evelyn>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)
    (<Relationship 'intimate' from (<Demo hollis>,) to (<Demo evelyn>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)
    (<Relationship 'business-partner' from (<Demo hollis>,) to (<Demo noah>,)>, <Relationship 'parent' from (<Demo evelyn>, <Demo noah>) to (<Demo katherine>,)>)


The relationships are as follows:

  evelyn \|-(sibling)-> katherine
  evelyn+noah \|-(parent)-> katherine
  noah \|-(parent)-> evelyn \|-(sibling)-> katherine
  jake \|-(intimate)-> evelyn \|-(sibling)-> katherine
  noah \|-(intimate)-> evelyn \|-(sibling)-> katherine
  hollis \|-(intimate)-> evelyn \|-(sibling)-> katherine
  jake \|-(nemesis)-> noah \|-(parent)-> katherine
  noah \|-(parent)-> evelyn \|-(parent)-> katherine
  jake \|-(intimate)-> evelyn \|-(parent)-> katherine
  noah \|-(intimate)-> evelyn \|-(parent)-> katherine
  hollis \|-(intimate)-> evelyn \|-(parent)-> katherine
  hollis \|-(business-partner)-> noah \|-(parent)-> katherine


It's important to note that nothing explodes when a cycle is found.
The result in such a case is just a special tuple that implements
ICircularRelationshipPath.  We can see this by looking at the simplest
cycles between ``evelyn`` and herself:

    >>> list(container.findRelationships(source=app['evelyn'],
    ...                                  target=app['evelyn'], maxDepth=2))
    [cycle(<Relationship 'client' from (<Demo evelyn>,) to (<Demo jake>,)>, <Relationship 'intimate' from (<Demo jake>,) to (<Demo evelyn>,)>)]


Acquisition Nonsense
--------------------

Zope 2 requires almost every object to support acquisition in order to
function (it is required for security and traversal).  Below we will perform
some sanity checks to ensure that the objects involved are wrapped in ways
that meet Zope 2's expectations:

    >>> list(container.findSources(target=app['katherine']))[0].aq_chain
    [<Demo evelyn>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(container.findTargets(source=app['hollis'],
    ...                            relation='business-partner'))[0].aq_chain
    [<Demo noah>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(list(container.findRelationships(source=app['evelyn'],
    ...                      target=app['katherine']))[0][0].targets)[0].aq_chain
    [<Demo katherine>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(list(container.findRelationships(source=app['evelyn'],
    ...                      target=app['katherine']))[0][0].sources)[0].aq_chain
    [<Demo evelyn>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]

As you can see, even as returned from the search the targets and
sources have their original wrapping.  Relationships are not wrapped,
though they can be explicitly wrapped with some available context when
security checks are needed.  The ``sources`` and ``targets``
attributes of a returned relationship will to have their original
wrapping as well, even after ghosting:

    >>> evelyn = list(container.findSources(target=app['katherine']))[0]
    >>> noah = list(container.findTargets(source=app['hollis'],
    ...                                   relation='business-partner'))[0]
    >>> rel = list(container.findRelationships(source=app['evelyn'],
    ...                          target=app['katherine']))[0][0]
    >>> sp = transaction.savepoint()
    >>> evelyn._p_deactivate()
    >>> noah._p_deactivate()
    >>> for _rel in container.values():
    ...    _rel._p_deactivate()
    ...    _rel.targets._p_deactivate()
    ...    _rel.sources._p_deactivate()
    >>> container._p_deactivate()
    >>> list(rel.targets)[0].aq_chain
    [<Demo katherine>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(container.findSources(target=app['katherine']))[0].aq_chain
    [<Demo evelyn>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(container.findTargets(source=app['hollis'],
    ...                            relation='business-partner'))[0].aq_chain
    [<Demo noah>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(list(container.findRelationships(source=app['evelyn'],
    ...                      target=app['katherine']))[0][0].targets)[0].aq_chain
    [<Demo katherine>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]

All of the wrappers are preserved except those on the ``sources`` and
``targets``, which for this reason mostly shouldn't be directly
depended on (at least not from code that requires security checks or
acquisition).

What happens when we create a relationship to an explicitly rewrapped object:

    >>> rel = Relationship((app['katherine'],),(app['jake'].__of__(container),))
    >>> container.add(rel)
    >>> list(rel.targets)[0].aq_chain
    [<Demo jake>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]
    >>> list(container.findTargets(source=app['katherine'],
    ...                            relation=None))[0].aq_chain
    [<Demo jake>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]

The retrieval via search returns the object only wrapped by its
original containment, regardless of how it was wrapped when used in
the relationship.  When we retrieve the relationship, the original wrapping
of ``sources`` and ``targets`` will be restored.

    >>> sp = transaction.savepoint()
    >>> rel._p_deactivate()
    >>> rel.sources._p_deactivate()
    >>> rel.targets._p_deactivate()
    >>> list(list(container.findRelationships(source=app['katherine'],
    ...                                relation=None))[0][0].targets)[0].aq_chain
    [<Demo jake>, <Application at >, <ZPublisher.BaseRequest.RequestContainer object at ...>]


    >>> tests.tearDown()
