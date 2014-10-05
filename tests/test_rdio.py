# future imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# stdlib imports
import os
import unittest

# third-party imports
from mock import patch

# local imports
from radiobabel import RdioClient
from radiobabel.errors import TrackNotFound, PlaylistNotFound
from radiobabel.test_utils import load_config, load_fixture


class LookupTests(unittest.TestCase):

    def setUp(self):
        load_config()
        self.client = RdioClient(os.environ['RDIO_CONSUMER_KEY'],
                                 os.environ['RDIO_CONSUMER_SECRET'])

    def test_lookup(self):
        """Rdio: Looking up a valid track (str) returns the expected data
        """
        track = self.client.lookup_track('t49660439')
        self.assertDictEqual(track, {
            'source_type': 'rdio',
            'source_id': 't49660439',
            'name': 'Shadow',
            'duration_ms': 231000,
            'preview_url': 'http://www.rdio.com/artist/Soja/album/'
                           'Amid_The_Noise_And_Haste/track/Shadow/',
            'uri': 'rdio://www.rdio.com/artist/Soja/album/'
                   'Amid_The_Noise_And_Haste/track/Shadow/',
            'track_number': 5,
            'image_small': 'http://img00.cdn2-rdio.com/album/8/2/e/'
                           '000000000045be28/4/square-200.jpg',
            'image_medium': 'http://img02.cdn2-rdio.com/album/8/2/e/'
                            '000000000045be28/4/square-400.jpg',
            'image_large': 'http://img00.cdn2-rdio.com/album/8/2/e/'
                           '000000000045be28/4/square-600.jpg',
            'artists': [
                {
                    'source_type': 'rdio',
                    'source_id': 'r47608',
                    'name': 'Soja',
                }
            ],
            'album': {
                'source_type': 'rdio',
                'source_id': 'a4570664',
                'name': 'Amid The Noise And Haste',
            },
        })

    def test_invalid_lookup(self):
        """Rdio: Looking up an invalid track raises the appropriate error
        """
        with self.assertRaises(TrackNotFound):
            self.client.lookup_track('asfasfasfas')


class SearchTests(unittest.TestCase):

    def setUp(self):
        load_config()
        self.client = RdioClient(os.environ['RDIO_CONSUMER_KEY'],
                                 os.environ['RDIO_CONSUMER_SECRET'])

    def test_search_returns_results(self):
        """Rdio: Test that search results are returned in the correct format.
        """
        results = self.client.search_tracks('one', limit=5)
        self.assertEquals(len(results), 5)

    def test_search_returns_no_results(self):
        """Rdio: Test that search with no results return empty list
        """
        results = self.client.search_tracks('kjasdkljadkljdklsjdklajs')
        self.assertEquals(len(results), 0)


class FetchAssociatedTrackTests(unittest.TestCase):

    def setUp(self):
        load_config()
        self.client = RdioClient(os.environ['RDIO_CONSUMER_KEY'],
                                 os.environ['RDIO_CONSUMER_SECRET'])

    def test_fetch_returns_result(self):
        """Rdio: Test that a fetch, returns a random track.
        """
        track_id = 't49660439'

        track = self.client.fetch_associated_track(track_id)

        self.assertNotEqual(track['source_id'], track_id)

    def test_fetch_returns_no_results(self):
        track_id = 't00000000'

        # utils.random_pick currently returns IndexError when passed []
        self.assertRaises(
            IndexError,
            lambda t_id: self.client.fetch_associated_track(t_id),
            track_id)


class PlaylistsTests(unittest.TestCase):

    def setUp(self):
        load_config()
        self.client = RdioClient(os.environ['RDIO_CONSUMER_KEY'],
                                 os.environ['RDIO_CONSUMER_SECRET'])

    def mocked_response(self, name):
        return load_fixture(name)['result']

    def test_playlists_returns_result(self):
        """Rdio: Test that looking up playlists from a user returns something.
        """
        user_id = 's6537051'

        with patch('radiobabel.backends.rdio._make_request',
                   return_value=self.mocked_response('rdio_playlists.json')):
            playlists = self.client.playlists(user_id, None)

        self.assertEquals(len(playlists), 2)
        self.assertEqual(playlists[0], {
            'source_type': 'rdio',
            'source_id': 'p7152205',
            'name': 'Reggae Reggae Sauce',
            'tracks': 162
        })
        self.assertEqual(playlists[1], {
            'source_type': 'rdio',
            'source_id': 'p7151600',
            'name': 'metaaaaaal',
            'tracks': 645
        })

    def test_playlists_return_no_results(self):
        user_id = 's9999999'

        self.assertEquals(self.client.playlists(user_id, None), [])

    def test_playlist_tracks_returns_result(self):
        """Rdio: Test that looking up tracks of a playlist returns tracks.
        """
        user_id = 's6537051'
        playlist_id = 'p11472759'

        with patch(
                'radiobabel.backends.rdio._make_request',
                return_value=self.mocked_response(
                    'rdio_playlist_tracks.json')):
            tracks = self.client.playlist_tracks(playlist_id, user_id, None)

        self.assertEqual(len(tracks), 2)

    def test_playlist_tracks_returns_no_results(self):
        user_id = 's000000'
        playlist_id = 'p00000000'

        # utils.random_pick currently returns IndexError when passed []
        self.assertRaises(
            PlaylistNotFound,
            lambda p_id, u_id: self.client.playlist_tracks(p_id, u_id, None),
            playlist_id, user_id
        )
