# future imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# stdlib imports
import logging
import copy

# third-party imports
from requests_oauthlib import OAuth1Session

# local imports
from radiobabel.errors import TrackNotFound, PlaylistNotFound
from .utils import random_pick

logger = logging.getLogger('radiobabel.backends.rdio')


def _make_request(client, data):
    """Make a HTTP request to the rdio API.
    """
    data = copy.deepcopy(data)
    extras = data.get('extras', '').split(',')
    if 'Track.bigIcon' not in extras:
        extras.append('Track.bigIcon')
    data['extras'] = ','.join(extras)
    response = client.post('http://api.rdio.com/1/', data=data)
    response.raise_for_status()
    return response.json()['result']


def _search(client, query, types, limit, offset):
    """Make a search query to rdio API.
    """
    return _make_request(client, data={'method': 'search', 'query': query,
                                       'types': types, 'count': limit,
                                       'start': offset})


def _transform_track(track):
    """Transform result into a format that more
    closely matches our unified API.
    """
    transformed_track = dict([
        ('source_type', 'rdio'),
        ('source_id', track['key']),
        ('name', track['name']),
        ('duration_ms', int(track['duration']) * 1000),
        ('preview_url', 'http://www.rdio.com' + track['url']),
        ('uri', 'rdio://www.rdio.com' + track['url']),
        ('track_number', track['trackNum']),
        ('image_small', track['icon']),
        ('image_medium',  track['icon400']),
        ('image_large',  track['bigIcon']),
    ])
    transformed_track['artists'] = [
        dict([
            ('source_type', 'rdio'),
            ('source_id', track['artistKey']),
            ('name', track['artist'])
        ]),
    ]
    transformed_track['album'] = dict([
        ('source_type', 'rdio'),
        ('source_id', track['albumKey']),
        ('name', track['album']),
    ])

    return transformed_track


def _transform_playlist(playlist):
    """Transform result into a format that more
    closely matches our unified API.
    """
    transformed_playlist = dict([
        ('source_type', 'rdio'),
        ('source_id', playlist['key']),
        ('name', playlist['name']),
        ('tracks', playlist['length']),
    ])
    return transformed_playlist


class RdioClient(object):

    def __init__(self, key, secret):
        """Initialise rdio API client.
        """
        self.client = OAuth1Session(key, secret)

    def lookup_track(self, track_id):
        """Lookup a single track using the rdio API
        """
        logger.info('Track lookup: {0}'.format(track_id))

        try:
            response = _make_request(self.client, data={'method': 'get',
                                                        'keys': track_id})
            track = next(iter(response.values()))
        except StopIteration:
            raise TrackNotFound('Rdio: {0}'.format(track_id))
        return _transform_track(track)

    def search_tracks(self, query, limit=200, offset=0):
        """Search for tracks using the rdio API
        """
        logger.info('Searching: Limit {0}, Offset {1}'.format(limit, offset))

        response = _search(self.client, query, 'Track', limit, offset)

        return [_transform_track(track) for track in response['results']]

    def fetch_associated_track(self, source_id):
        """Fetch a random associated track, using the rdio API.
        """
        radio_id = 'sr' + source_id[1:]

        response = _make_request(self.client, data={'method': 'get',
                                                    'keys': radio_id})

        try:
            radio = next(iter(response.values()))

            tracks = [_transform_track(track) for track in radio['tracks']]

        except StopIteration:
            tracks = []

        track = random_pick(tracks)

        return track

    def playlists(self, user_id, token):
        """Lookup user playlists using the rdio Web API

        Returns standard radiobabel playlist list response.
        """

        playlists = _make_request(self.client, data={
            'method': 'getUserPlaylists', 'user': user_id
        })

        transform_playlists = []
        for playlist in playlists:
            transform_playlists.append(_transform_playlist(playlist))

        return transform_playlists

    def playlist_tracks(self, playlist_id, user_id, token, limit=20, offset=0):
        """Lookup user playlists using the rdio Web API

        Returns standard radiobabel track list response.
        """
        logger.info('Playlist tracks lookup: {0}'.format(user_id))

        try:
            response = _make_request(self.client, data={'method': 'get',
                                                        'keys': playlist_id,
                                                        'extras': 'tracks'})
            playlist = next(iter(response.values()))
        except StopIteration:
            raise PlaylistNotFound('Rdio: {0}'.format(playlist_id))

        return [_transform_track(track) for track in playlist['tracks']]
