import urllib
import urllib2
import json
import difflib
import pylast


class iTunesAlbumArt(object):
    def __init__(self):
        self.base_url = 'https://itunes.apple.com/search'
        self.limit = 50

    def _form_url(self, artist):
        args_dict = {'limit': self.limit,
                     'term': artist}
        args_string = urllib.urlencode(args_dict)
        search_url = self.base_url + '?' + args_string
        return search_url

    def _get_largest_pic_url(self, pic_100_url):
        resolutions_to_try = [
            '1500x1500',
            '1200x1200',
            '900x900',
            '600x600',
            '300x300',
            '100x100'
        ]
        head, _, tail = pic_100_url.rpartition('100x100')
        for resolution in resolutions_to_try:
            try:
                potential_pic_url = head + resolution + tail
                urllib2.urlopen(potential_pic_url)
            except ValueError:
                # URL not well formatted
                continue
            except urllib2.URLError:
                # Doesn't seem to exist
                continue
            break
        return potential_pic_url

    def _find_album(self, tracks_by_artist, album):
        for track in tracks_by_artist:
            if track.get('collectionName', None):
                difference = difflib.SequenceMatcher(None,
                                                     track['collectionName'],
                                                     album).ratio()
                if difference > 0.5:
                    return track
        return None

    def find_art(self, artist, album):
        search_url = self._form_url(artist)
        response = urllib2.urlopen(search_url)
        response_json = json.loads(response.read())
        if response_json['resultCount'] == 0:
            return None
        tracks = response_json['results']
        track = self._find_album(tracks, album)
        if not track:
            return None
        large_picture_url = self._get_largest_pic_url(track['artworkUrl100'])
        return large_picture_url


class LastFMAlbumArt(object):
    """
    Trivially stupid stub

    I just wanted to make it look consistant with the iTunes one
    """
    def __init__(self, key=None, secret=None):
        if not key or not secret:
            print 'Last.fm API Key and Secret required'
            return None
        self.api = pylast.LastFMNetwork(
            api_key=key,
            api_secret=secret
        )

    def find_art(self, artist, album_name):
        try:
            album = self.api.get_album(artist, album_name)
            pic_url = album.get_cover_image(pylast.COVER_EXTRA_LARGE)
        except pylast.WSError:
            pic_url = None
        return pic_url
