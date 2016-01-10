import logging

from ladygeek.graph.node_wrapper import NodeWrapper, RelationshipMeta, NoRelationshipExists


log = logging.getLogger(__name__)

class User(NodeWrapper):
    UNIQUE_KEY = "id"
    RELATIONSHIPS = {
        "handle": RelationshipMeta("In", "IS_USER", "Handle", False),
        "followers": RelationshipMeta("Out", "FOLLOWS", "User", True),
        "following": RelationshipMeta("In", "FOLLOWS", "User", False),
        "tweets": RelationshipMeta("Out", "TWEETS", "Tweet", True)
    }

    def get_follower_tweets(self):
        for f in self.get_followers():
            yield from f.get_tweets()

    def get_company(self):
        return self.get_handle().get_company()


class Handle(NodeWrapper):
    UNIQUE_KEY = "name"
    RELATIONSHIPS = {
        "user": RelationshipMeta("Out", "IS_USER", "User", False),
        "company": RelationshipMeta("In", "TWEETS_AS", "Company", False),
    }


class Company(NodeWrapper):
    UNIQUE_KEY = "name"
    RELATIONSHIPS = {
        "handles": RelationshipMeta("Out", "TWEETS_AS", "Handle", True)
    }

    def get_follower_tweets(self):
        for h in self.get_handles():
            u = h.get_user()
            for f in u.get_followers():
                yield from f.get_tweets()

    def get_tweets(self):
        for h in self.get_handles():
            u = h.get_user()
            yield from u.get_tweets()


class Index(NodeWrapper):
    UNIQUE_KEY = "name"
    RELATIONSHIPS = {
        "companies": RelationshipMeta("Out", "INCLUDES", "Company", True)
    }

    def get_all_users(self, members=True, followers=True):
        if not(members or followers):
            return [].__iter__()
        for c in self.get_companies():
            for h in c.get_handles():
                try:
                    u = h.get_user()
                except NoRelationshipExists:
                    log.warn("No user data for %s" % h["name"])
                    continue
                if members:
                    yield u
                if followers:
                    yield from u.get_followers()

    def get_twitter_ids(self, members=True, followers=True):
        return (u["id"] for u in self.get_all_users(members, followers))



class Tweet(NodeWrapper):
    UNIQUE_KEY = "id"
    RELATIONSHIPS = {
        "user": RelationshipMeta("In", "TWEETS", "User", True)
    }


if __name__ == "__main__":
    print(repr(User))
    print(repr(Handle))