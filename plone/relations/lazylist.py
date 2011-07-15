from itertools import chain
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

class LazyList(object):
    """A class that makes an iterator look like a sequence,
    it only unspools the iterator as needed (no infinite iterators please),
    to perform its operations.

    Let's test this out, first we create lazy lists from existing
    iterators::

        >>> iter1 = xrange(20)
        >>> list1 = LazyList(iter1)
        >>> def iter2_func():
        ...     for i in xrange(20):
        ...         yield i
        >>> list2 = LazyList(iter2_func())

    First we ensure that we have a working len(), and that calling it
    doesn't result in unspooling the iterator unless necessary::

        >>> len(list1)
        20
        >>> list1._list is None
        True
        >>> list1[5]
        5
        >>> list1._list
        [0, 1, 2, 3, 4, 5]
        >>> list1[2:4]
        [2, 3]
        >>> list1._list
        [0, 1, 2, 3, 4, 5]
        >>> list1[-3]
        17
        >>> len(list1._list)
        20

    Now the iterator is entirely unspooled::

        >>> [i for i in list1._iter]
        []
        >>> list1._list == list(list1)
        True

    Our generator function behaves the same, except that using len() unspools
    it entirely::

        >>> list2[:5]
        [0, 1, 2, 3, 4]
        >>> list2._list
        [0, 1, 2, 3, 4]
        >>> list2[4:7]
        [4, 5, 6]
        >>> list2._list
        [0, 1, 2, 3, 4, 5, 6]
        >>> len(list2)
        20
        >>> len(list2._list)
        20

    We can also add these lists, if they are both fully unspooled we
    get a normal list::

        >>> list3 = list2 + list1
        >>> isinstance(list3, list)
        True
        >>> len(list3)
        40

    Otherwise we get another LazyList, note that when we slice past
    the end of the list the whole list gets resolved as expected::

        >>> list4 = LazyList(iter2_func())
        >>> list5 = list4 + list1
        >>> isinstance(list5, LazyList)
        True
        >>> list5[19:21]
        [19, 0]
        >>> len(list5._list)
        21
        >>> list5[:53] == list(list5)
        True
        >>> len(list5._list)
        40

    We can also "reverse" the list in place, which will unspool the
    whole thing::

        >>> list6 = LazyList(iter2_func())
        >>> list6[6]
        6
        >>> list6.reverse()
        >>> list6[6]
        13
        >>> len(list6._list)
        20

    We can also apply the reversed built-in to the list::

        >>> list7 = LazyList(iter2_func())
        >>> r = reversed(list7)
        >>> r.next()
        19
        >>> list7[0]
        0
        >>> len(list7._list)
        20

    We also have truth testing which doesn't unspool the list::

        >>> list8 = LazyList(iter2_func())
        >>> bool(list8)
        True
        >>> len(list8._list)
        1

   We can also handle regular lists as input::

        >>> list9 = LazyList([1,2,3,4,5])
        >>> len(list9._list)
        5
        >>> list9[0]
        1
        >>> list9[1:2]
        [2]

    """
    __allow_access_to_unprotected_subobjects__ = True
    _finished = False
    _list = None

    def __init__(self, initlist):
        self._orig_iter = initlist
        self._iter = iter(initlist)
        if isinstance(initlist, (list, tuple)):
            # skip extra processing when we get a list or tuple
            self._list = list(initlist)
            self._finished = True

    @property
    def _pos(self):
        try:
            return len(self._list) - 1
        except TypeError:
            # the list isn't initialized
            return -1

    def __iter__(self):
        # iterate over our internal list first
        # then the iterator
        if self._list is None:
            self._list = []
        for item in self._list:
            yield item
        if not self._finished:
            for item in self._iter:
                self._list.append(item)
                yield item
            else:
                # We completed the final iteration
                self._finished = True

    def _extract_to(self, end):
        if self._finished or (self._pos >= end and end >= 0):
            pass
        elif end < 0:
            # We need to unwrap the whole thing
            thelist = [i for i in self] # invokes __iter__ which sets _list
        else:
            num_iters = end - self._pos
            # continue where we left off
            if self._list is None:
                self._list = []
            for i, item in enumerate(self._iter):
                self._list.append(item)
                if i+1 >= num_iters:
                    break
            else:
                self._finished = True
        return self._list

    def __len__(self):
        # use the native __len__ if available
        if hasattr(self._orig_iter, '__len__'):
            return len(self._orig_iter)
        # Otherwise unspool the whole thing
        return len(self._extract_to(-1))

    def __getitem__(self, i):
        return self._extract_to(i)[i]

    def __getslice__(self, i, j):
        return self._extract_to(j-1)[i:j]

    def __reversed__(self):
        return reversed(self._extract_to(-1))

    def __add__(self, other):
        if self._finished and getattr(other, '_finished', False):
            return self._list + other._list
        return self.__class__(chain(self.__iter__(), other.__iter__()))

    def reverse(self):
        self._extract_to(-1).reverse()

    def __nonzero__(self):
        """Override this to avoid unspooling the whole list for a len check"""
        return bool(self._extract_to(0))


class LazyResolvingList(object):
    """A sequence class that acts like a list by lazily resolving
    a set of tokens, assumes tokens are intids, a custom resolver method
    can be passed in, it must take accept a single token and return
    a value.

    To see it in action we make a trivial resolver with a dictionary lookup::

        >>> TABLE = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f',
        ...          6: 'g', 7: 'h', 8: 'i', 9: 'j'}
        >>> resolver = TABLE.get
        >>> counter = 0
        >>> def resolver(x):
        ...     global counter
        ...     counter += 1
        ...     return TABLE.get(x)
        >>> gen = xrange(10)
        >>> list1 = LazyResolvingList(gen, resolver)

    Any attempt to access the list should resolve the elements on demand,
    we will check the counter to ensure that we only resolve the elements
    that are requested::

        >>> counter
        0
        >>> list1[1]
        'b'
        >>> counter
        1
        >>> slice1 = list1[2:5]
        >>> isinstance(slice1, LazyResolvingList)
        True
        >>> counter
        1
        >>> list(slice1)
        ['c', 'd', 'e']
        >>> counter
        4
        >>> iter(list1).next()
        'a'
        >>> counter
        5
        >>> len(list1)
        10
        >>> counter
        5
        >>> list1[-1]
        'j'
        >>> counter
        6

    We can also add these lists together::

        >>> def gen2_func():
        ...     for i in xrange(10):
        ...         yield i
        >>> gen2 = gen2_func()
        >>> list2 = LazyResolvingList(gen, resolver)
        >>> list3 = LazyResolvingList(gen2, resolver)
        >>> list4 = list3 + list2
        >>> counter
        6
        >>> slice2 = list4[9:11]
        >>> counter
        6
        >>> isinstance(slice2, LazyResolvingList)
        True
        >>> list(slice2)
        ['j', 'a']
        >>> counter
        8
        >>> len(list4)
        20

    There are also some dictionary like methods which can be used to
    get at the tokens themselves::

        >>> list(list1.keys())
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list(list1.values())
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        >>> list(list1.items()) == zip(list(list1.keys()), list(list1.values()))
        True

    """
    __allow_access_to_unprotected_subobjects__ = True
    _util_method = None

    def __init__(self, initlist, resolver=None):
        self._data = LazyList(initlist)
        self._resolver = resolver

    def _resolve(self, token):
        """default resolver"""
        if self._resolver is not None:
            return self._resolver(token)
        if self._util_method is None:
            self._util_method = getUtility(IIntIds).getObject
        return self._util_method(token)

    def __len__(self):
        """This unspools the whole list""" 
        return len(self._data)

    def __iter__(self):
        """resolves the tokens"""
        for item in self._data:
            yield self._resolve(item)

    def __getitem__(self, i):
        return self._resolve(self._data[i])

    def __getslice__(self, i, j):
        """Returns an instance of this class containing the desired slice"""
        return self.__class__(self._data[i:j], self._resolver)

    def __add__(self, other):
        """Dumb add method that assumes identical resolvers"""
        assert self._resolver == getattr(other, '_resolver', None), \
                   "Both items must use the same resolver method"
        return self.__class__(self._data + other._data, self._resolver)

    def keys(self):
        return iter(self._data)

    def values(self):
        return iter(self)

    def items(self):
        for item in self._data:
            yield (item, self._resolve(item))

    def __nonzero__(self):
        return bool(self._data)


def lazyresolver(resolver=None, resolver_name=None):
    def wrapper(func, _resolver=resolver, _resolver_name=resolver_name):
        def resolver_func(self, *args, **kw):
            resolver = _resolver
            if not resolver and _resolver_name is not None:
                resolver = getattr(self, _resolver_name)
            return LazyResolvingList(func(self, *args, **kw),
                                     resolver = resolver)
        return resolver_func
    return wrapper

intidresolver = lazyresolver()
