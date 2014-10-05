"""radiobabel

Interact with a number of online music services using a single unified API.
"""
# local imports
from .backends.soundcloud import SoundcloudClient
from .backends.spotify import SpotifyClient
from .backends.youtube import YoutubeClient
from .backends.rdio import RdioClient

__version__ = '0.1.0'
__author__ = 'Paddy Carey <patrick@rehabstudio.com>'
__maintainer__ = 'Paddy Carey <patrick@rehabstudio.com>'

__all__ = ['SoundcloudClient', 'SpotifyClient', 'YoutubeClient', 'RdioClient']
