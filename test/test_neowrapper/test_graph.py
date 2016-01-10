import unittest
from ladygeek.graph.client import get_graph
from ladygeek.graph.entities import Index, Company


class TestGraph(unittest.TestCase):

    def test_dev_graph(self):
        g = get_graph("dev")
        c = Company.new(g, {"name":"foo"})

if __name__ == '__main__':
    unittest.main()