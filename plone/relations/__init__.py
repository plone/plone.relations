# A tiny monkey patch due to some re-organization of future BTree modules
try:
    from BTrees.OOBTree import BTree
except ImportError:
    import BTrees.OOBTree
    import BTrees.IOBTree
    import BTrees.OIBTree
    import BTrees.IIBTree
    import BTrees.IFBTree
    BTrees.OOBTree.BTree = BTrees.OOBTree.OOBTree
    BTrees.OOBTree.Set = BTrees.OOBTree.OOSet
    BTrees.OOBTree.Bucket = BTrees.OOBTree.OOBucket
    BTrees.OOBTree.TreeSet = BTrees.OOBTree.OOTreeSet
    BTrees.IOBTree.BTree = BTrees.IOBTree.IOBTree
    BTrees.IOBTree.Set = BTrees.IOBTree.IOSet
    BTrees.IOBTree.Bucket = BTrees.IOBTree.IOBucket
    BTrees.IOBTree.TreeSet = BTrees.IOBTree.IOTreeSet
    BTrees.OIBTree.BTree = BTrees.OIBTree.OIBTree
    BTrees.OIBTree.Set = BTrees.OIBTree.OISet
    BTrees.OIBTree.Bucket = BTrees.OIBTree.OIBucket
    BTrees.OIBTree.TreeSet = BTrees.OIBTree.OITreeSet
    BTrees.IIBTree.BTree = BTrees.IIBTree.IIBTree
    BTrees.IIBTree.Set = BTrees.IIBTree.IISet
    BTrees.IIBTree.Bucket = BTrees.IIBTree.IIBucket
    BTrees.IIBTree.TreeSet = BTrees.IIBTree.IITreeSet
    BTrees.IFBTree.BTree = BTrees.IFBTree.IFBTree
    BTrees.IFBTree.Set = BTrees.IFBTree.IFSet
    BTrees.IFBTree.Bucket = BTrees.IFBTree.IFBucket
    BTrees.IFBTree.TreeSet = BTrees.IFBTree.IFTreeSet
