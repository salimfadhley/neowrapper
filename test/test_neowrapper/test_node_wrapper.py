import unittest

from ladygeek.graph.node_wrapper import NodeMeta

class TestEntities(unittest.TestCase):

    def testGetGetterName(self):
        name = "foo"
        multiple = False
        self.assertEqual(NodeMeta.get_getter_name(name), 'get_foo')
