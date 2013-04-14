"""
This module defines export functions for decision trees.
"""

# Authors: Brian Holt,
#          Peter Prettenhofer,
#          Satrajit Ghosh,
#          Gilles Louppe,
#          Noel Dawe
# License: BSD Style.

from ..externals import six
from . import _tree


def export_graphviz(decision_tree, out_file="tree.dot", feature_names=None):
    """Export a decision tree in DOT format.

    This function generates a GraphViz representation of the decision tree,
    which is then written into `out_file`. Once exported, graphical renderings
    can be generated using, for example::

        $ dot -Tps tree.dot -o tree.ps      (PostScript format)
        $ dot -Tpng tree.dot -o tree.png    (PNG format)

    Parameters
    ----------
    decision_tree : decision tree classifier
        The decision tree to be exported to graphviz.

    out_file : file object or string, optional (default="tree.dot")
        Handle or name of the output file.

    feature_names : list of strings, optional (default=None)
        Names of each of the features.

    Returns
    -------
    out_file : file object
        The file object to which the tree was exported.  The user is
        expected to `close()` this object when done with it.

    Examples
    --------
    >>> import os
    >>> from sklearn.datasets import load_iris
    >>> from sklearn import tree

    >>> clf = tree.DecisionTreeClassifier()
    >>> iris = load_iris()

    >>> clf = clf.fit(iris.data, iris.target)
    >>> import tempfile
    >>> export_file = tree.export_graphviz(clf,
    ...     out_file='test_export_graphvix.dot')
    >>> export_file.close()
    >>> os.unlink(export_file.name)
    """
    def node_to_str(tree, node_id):
        value = tree.value[node_id]
        if tree.n_outputs == 1:
            value = value[0, :]

        if tree.children_left[node_id] == _tree.TREE_LEAF:
            return "error = %.4f\\nsamples = %s\\nvalue = %s" \
                   % (tree.init_error[node_id],
                      tree.n_samples[node_id],
                      value)
        else:
            if feature_names is not None:
                feature = feature_names[tree.feature[node_id]]
            else:
                feature = "X[%s]" % tree.feature[node_id]

            return "%s <= %.4f\\nerror = %s\\nsamples = %s\\nvalue = %s" \
                   % (feature,
                      tree.threshold[node_id],
                      tree.init_error[node_id],
                      tree.n_samples[node_id],
                      value)

    def recurse(tree, node_id, parent=None):
        if node_id == _tree.TREE_LEAF:
            raise ValueError("Invalid node_id %s" % _tree.TREE_LEAF)

        left_child = tree.children_left[node_id]
        right_child = tree.children_right[node_id]

        # Add node with description
        out_file.write('%d [label="%s", shape="box"] ;\n' %
                       (node_id, node_to_str(tree, node_id)))

        if parent is not None:
            # Add edge to parent
            out_file.write('%d -> %d ;\n' % (parent, node_id))

        if left_child != _tree.TREE_LEAF:  # and right_child != _tree.TREE_LEAF
            recurse(tree, left_child, node_id)
            recurse(tree, right_child, node_id)

    if isinstance(out_file, six.string_types):
        if six.PY3:
            out_file = open(out_file, "w", encoding="utf-8")
        else:
            out_file = open(out_file, "wb")

    out_file.write("digraph Tree {\n")
    if isinstance(decision_tree, _tree.Tree):
        recurse(decision_tree, 0)
    else:
        recurse(decision_tree.tree_, 0)
    out_file.write("}")

    return out_file