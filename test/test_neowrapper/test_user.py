import unittest
from ladygeek.graph.client import get_graph_url
from ladygeek.graph.entities import User

from py2neo import Graph

class TestUser(unittest.TestCase):

    USER_DATA = {'contributors_enabled': False,
                 'created_at': 'Fri Jun 12 11:13:21 +0000 2009',
                 'default_profile': False,
                 'default_profile_image': False,
                 'description': 'We are the UK’s leading energy supplier and committed to '
                                'looking after your world. For Emergency numbers visit '
                                'http://t.co/GVkMDCUzW3',
                 'entities': {'description': {'urls': [{'display_url': 'britishgas.co.uk/emergency',
                                                        'expanded_url': 'http://www.britishgas.co.uk/emergency',
                                                        'indices': [111, 133],
                                                        'url': 'http://t.co/GVkMDCUzW3'}]},
                              'url': {'urls': [{'display_url': 'britishgas.co.uk/the-source',
                                                'expanded_url': 'http://www.britishgas.co.uk/the-source',
                                                'indices': [0, 22],
                                                'url': 'http://t.co/rlasQ9hHeu'}]}},
                 'favourites_count': 431,
                 'follow_request_sent': False,
                 'followers_count': 36081,
                 'following': False,
                 'friends_count': 4774,
                 'geo_enabled': True,
                 'id': 46630225,
                 'id_str': '46630225',
                 'is_translation_enabled': False,
                 'is_translator': False,
                 'lang': 'en',
                 'listed_count': 400,
                 'location': 'Staines, Middlesex',
                 'name': 'British Gas ',
                 'notifications': False,
                 'profile_background_color': '00AEDE',
                 'profile_background_image_url': 'http://pbs.twimg.com/profile_background_images/831694128/7187a2d2a890b67c21ae04c18861f5b9.jpeg',
                 'profile_background_image_url_https': 'https://pbs.twimg.com/profile_background_images/831694128/7187a2d2a890b67c21ae04c18861f5b9.jpeg',
                 'profile_background_tile': False,
                 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/46630225/1400584801',
                 'profile_image_url': 'http://pbs.twimg.com/profile_images/552048129055289344/6oPZvR3T_normal.jpeg',
                 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/552048129055289344/6oPZvR3T_normal.jpeg',
                 'profile_link_color': '1890C4',
                 'profile_location': None,
                 'profile_sidebar_border_color': 'FFFFFF',
                 'profile_sidebar_fill_color': 'D9EDF9',
                 'profile_text_color': '333333',
                 'profile_use_background_image': True,
                 'protected': False,
                 'screen_name': 'BritishGas',
                 'status': {'contributors': None,
                            'coordinates': None,
                            'created_at': 'Mon Mar 02 18:45:18 +0000 2015',
                            'entities': {'hashtags': [],
                                         'media': [{'display_url': 'pic.twitter.com/ec4iusBe4Q',
                                                    'expanded_url': 'http://twitter.com/BritishGas/status/572467734367191041/photo/1',
                                                    'id': 572425479120007168,
                                                    'id_str': '572425479120007168',
                                                    'indices': [108, 130],
                                                    'media_url': 'http://pbs.twimg.com/media/B_Gp8L9UsAAe8ap.png',
                                                    'media_url_https': 'https://pbs.twimg.com/media/B_Gp8L9UsAAe8ap.png',
                                                    'sizes': {'large': {'h': 500,
                                                                        'resize': 'fit',
                                                                        'w': 1000},
                                                              'medium': {'h': 300,
                                                                         'resize': 'fit',
                                                                         'w': 600},
                                                              'small': {'h': 170,
                                                                        'resize': 'fit',
                                                                        'w': 340},
                                                              'thumb': {'h': 150,
                                                                        'resize': 'crop',
                                                                        'w': 150}},
                                                    'type': 'photo',
                                                    'url': 'http://t.co/ec4iusBe4Q'}],
                                         'symbols': [],
                                         'urls': [],
                                         'user_mentions': []},
                            'favorite_count': 4,
                            'favorited': False,
                            'geo': None,
                            'id': 572467734367191041,
                            'id_str': '572467734367191041',
                            'in_reply_to_screen_name': None,
                            'in_reply_to_status_id': None,
                            'in_reply_to_status_id_str': None,
                            'in_reply_to_user_id': None,
                            'in_reply_to_user_id_str': None,
                            'lang': 'en',
                            'place': None,
                            'possibly_sensitive': False,
                            'retweet_count': 3,
                            'retweeted': False,
                            'source': '<a href="https://ads.twitter.com" '
                                      'rel="nofollow">Twitter Ads</a>',
                            'text': 'Afraid of the dust bunny lurking behind your fridge? '
                                    'Check out our guide to cleaning up those fridge coils: '
                                    'http://t.co/ec4iusBe4Q',
                            'truncated': False},
                 'statuses_count': 13664,
                 'time_zone': 'London',
                 'url': 'http://t.co/rlasQ9hHeu',
                 'utc_offset': 0,
                 'verified': True}

    def setUp(self):
        self.g = Graph(get_graph_url("dev"))

    def tearDown(self):
        self.g.delete_all()

    def testAddNewUser(self):
        u = User.new(self.g, properties=self.USER_DATA)
        u.get_followers()


if __name__ == '__main__':
    unittest.main()
