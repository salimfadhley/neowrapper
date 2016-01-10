import unittest

from neowrapper.client import get_graph
from neowrapper.node_wrapper import MissingProperty
from py2neo import Node, Relationship
from ladygeek.graph.entities import Handle, Company, Index, Tweet, User


class TestEntities(unittest.TestCase):
    def setUp(self):
        self.g = get_graph("dev")

    def tearDown(self):
        self.g.delete_all()

    def testThingNotExists(self):
        self.assertFalse(Company.exists(self.g, {"name": "fooCorp"}))

    def testThingDoesExist(self):
        Company.new(self.g, {"name": "IBM"})
        self.assertTrue(Company.exists(self.g, {"name": "IBM"}))

    def testAccessTheGraph(self):
        c = Company.new(self.g, {"name": "IBM"})
        self.assertEqual(c.g, self.g)

    def testAddTweet(self):
        Tweet.new(self.g, {"id": 123456})

    def testMergeUser(self):
        u0 = User.new(self.g, {"id": 123456, "screen_name": "fluffer1"})
        u1 = User.new(self.g, {"id": 123456})

        self.assertEqual(u0["screen_name"], u1["screen_name"])
        self.assertEqual(u1["screen_name"], "fluffer1")

    def testAddUserWithExtraAttrs(self):
        u0 = User.new(self.g, {"id": 123456, "screen_name": "fluffer1"})
        u1 = User.find_one(self.g, {"screen_name": "fluffer1"})
        self.assertEqual(u0, u1)

    def testGraphPush(self):
        u = User.new(self.g, {"id": 1234, "name": "Froo Froo"})
        u.push()

    def testGetCompanyFromHandle(self):
        company = Node("Company", name="IBM")
        handle = Node("Handle", name="@ibm")
        rel = Relationship(company, "TWEETS_AS", handle)
        self.g.create(rel)
        H = Handle(handle)
        C = H.get_company()
        self.assertIsInstance(C, Company)

    def testGetHandlesForCompany0(self):
        company = Node("Company", name="IBM")
        handle0 = Node("Handle", name="@ibm")
        handle1 = Node("Handle", name="@ibm_support")
        rel0 = Relationship(company, "TWEETS_AS", handle0)
        rel1 = Relationship(company, "TWEETS_AS", handle1)
        self.g.create(rel0)
        self.g.create(rel1)
        C = Company(company)
        handles = list(C.get_handles())
        self.assertIsInstance(handles[0], Handle)
        self.assertIsInstance(handles[1], Handle)

    def testGetUsersForHandle0(self):
        handle0 = Node("Handle", name="@ibm")
        user0 = Node("User", name="ibm", id=12345)
        rel0 = Relationship(handle0, "IS_USER", user0)
        self.g.create(rel0)
        H = Handle(handle0)
        U = H.get_user()
        self.assertIsInstance(U, User)

    def testGetUsersForHandle1(self):
        handle0 = Handle.new(self.g, {"name": "ibm"})
        handle0.add_user({"id": 12345, "name": "hello world"})

        del handle0

        H = Handle.find_one(self.g, {"name": "ibm"})
        U = H.get_user()
        self.assertIsInstance(U, User)
        self.assertEqual(U["name"], "hello world")

    def testGetCompaniesForIndex(self):
        COMPANY_NAMES = ["IBM", "JCB", "ICL", "JPM"]
        i = Node("Index", name="Test Index")
        I = Index(i)
        for company_name in COMPANY_NAMES:
            c = Node("Company", name=company_name)
            r = Relationship(i, "INCLUDES", c)
            self.g.create(r)
        self.assertEqual(len(list(I.get_companies())), 4)

    def testGetCompanyForUser(self):
        c = Company.new(self.g, {"name": "FooCorp"})
        h = c.add_handles([{'name': 'foo_corp'}])[0]
        u = h.add_user({'screen_name': 'foo_corp', 'id': 1234})
        self.assertEqual(u.get_company(), c)


    def testCreateIndexNode(self):
        i = Index.new(self.g, {"name": "Test Index 2"})
        self.assertIsInstance(i, Index)
        self.assertEqual(i.n.properties['name'], "Test Index 2")

    def testCreateAndFindIndex(self):
        index_name = "Test Index 4"
        i = Index.new(self.g, {"name": index_name}).push()
        ix = Index.find_one(self.g, dict(name=index_name))
        self.assertEqual(i, ix)


    def testAddCompanyToIndex(self):
        i = Index.new(self.g, {"name": "Test Index 6"})
        self.assertEqual(len(list(i.get_companies())), 0)
        i.add_companies([{'name': "CBS"}, {'name': 'ABC'}])
        self.assertEqual(len(list(i.get_companies())), 2)


    def testVerifyThatTweetsAreUniqueById(self):
        tw = {"id": 123456}
        self.assertEqual(len(list(Tweet.find(self.g, tw))), 0)
        Tweet.new(self.g, tw)
        self.assertEqual(len(list(Tweet.find(self.g, tw))), 1)
        Tweet.new(self.g, tw)
        self.assertEqual(len(list(Tweet.find(self.g, tw))), 1)


    def testVerifyThatComplexTweetsAreUniqueById(self):
        tw = {"id": 123456, "text": "Hello world!"}
        short_tw = {"id": 123456}
        self.assertEqual(len(list(Tweet.find(self.g, short_tw))), 0)
        Tweet.new(self.g, short_tw)  # Just the ID
        self.assertEqual(len(list(Tweet.find(self.g, short_tw))), 1)
        Tweet.new(self.g, tw)
        self.assertEqual(len(list(Tweet.find(self.g, short_tw))), 1)

    def testAddOrNewCompanyToIndex(self):
        i = Index.new(self.g, {"name": "Test Index 3"})

        self.assertEqual(len(list(i.get_companies())), 0)

        i.add_companies([{'name': "CBS"}])
        i.add_companies([{'name': "CBS"}], unique=True)

        self.assertEqual(len(list(i.get_companies())), 1)

    def testInvalidUser(self):
        with self.assertRaises(MissingProperty):
            User.new(self.g, {"fod": "foo"})

    def testAddUniqueNode(self):
        self.assertEqual(len(list(Index.find(self.g, {"name": "Test Index 6"}))), 0)

        Index.new(self.g, {"name": "Test Index 6"}, unique=True)
        self.assertEqual(len(list(Index.find(self.g, {"name": "Test Index 6"}))), 1)

        Index.new(self.g, {"name": "Test Index 6"}, unique=True)
        self.assertEqual(len(list(Index.find(self.g, {"name": "Test Index 6"}))), 1)

    def testSample(self):
        u1 = User.new(self.g, {"id": "CH"})
        u2 = User.new(self.g, {"id": "Cl"})
        u3 = User.new(self.g, {"id": "C"})

        users = User.sample(self.g, n=2)
        self.assertEqual(len(users), 2)

    def testAddedNodesWrapActualNodes(self):
        i = Index.new(self.g, {"name": "Test Index"})
        c = i.add_companies([{"name": "Fluffer"}])[0]
        self.assertIsInstance(c.n, Node)

    def testWrappedNodeMustBeSomething(self):
        with self.assertRaises(ValueError):
            Index(None)

    def testGetTweets(self):
        u = User.new(self.g, {"id": "CH"})
        u.add_tweets([
            {"id":1, "text":"tw0"},
            {"id":2, "text":"tw1"},
            {"id":3, "text":"tw2"},
            {"id":4, "text":"tw3"},
        ])

        result = set(t["text"] for t in u.get_tweets())
        self.assertEqual(result, set(["tw0", "tw1", "tw2", "tw3"]))

    def testGetCompanyTweets(self):
        c = Company.new(self.g, {"name": "MyCompany"})
        h = c.add_handles([{"name": "my_company"}])[0]
        u = h.add_user({"id": "CH"})
        u.add_tweets([
            {"id": 1, "text": "tw0"},
            {"id": 2, "text": "tw1"},
            {"id": 3, "text": "tw2"},
            {"id": 4, "text": "tw3"},
        ])

        result = set(t["text"] for t in c.get_tweets())
        self.assertEqual(result, set((["tw0", "tw1", "tw2", "tw3"])))

    def testGetCompanyFollowerTweets(self):
        c = Company.new(self.g, {"name": "MyCompany"})
        h = c.add_handles([{"name": "my_company"}])[0]
        mu = h.add_user({"id": "CH"})
        u = mu.add_followers([{"id": 2345, "screen_name": "follower"}, ])[0]
        u.add_tweets([
            {"id": 1, "text": "tw0"},
            {"id": 2, "text": "tw1"},
            {"id": 3, "text": "tw2"},
            {"id": 4, "text": "tw3"},
        ])
        result = set(t["text"] for t in c.get_follower_tweets())
        self.assertEqual(result, set(["tw0", "tw1", "tw2", "tw3"]))


    def testGetFollowerTweets(self):

        mu = User.new(self.g, {"id":1234, "screen_name":"member"})
        u =mu.add_followers( [{"id": 2345, "screen_name":"follower"}, ])[0]
        u.add_tweets([
            {"id":1, "text":"tw0"},
            {"id":2, "text":"tw1"},
            {"id":3, "text":"tw2"},
            {"id":4, "text":"tw3"},
            ])

        result = set(t["text"] for t in mu.get_follower_tweets())
        self.assertEqual(result, set(["tw0", "tw1", "tw2", "tw3"]))


if __name__ == '__main__':
    unittest.main()
