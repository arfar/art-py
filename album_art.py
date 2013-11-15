import os
import sys
import apis
import urllib2
from mutagen.flac import FLAC
from mutagen.mp3 import MP3


class AlbumArtGrabber(object):
    def __init__(self, root_directory='.', cover_name='cover.'):
        self.last_fm = apis.LastFMAlbumArt(
            key='8c95f92a46b2dedce897ebbd46e6e575',
            secret='93444c81db008d7de67fa7c19900429f'
        )
        self.itunes = apis.iTunesAlbumArt()
        self.root_directory = root_directory
        self.cover_name = cover_name
        self.image_exts = [
            'jpg',
            'gif',
            'png'
        ]
        self.music_exts = [
            'mp3',
            'flac'
        ]

    def _cover_already_exists(self, files):
        for a_file in files:
            if a_file.startswith(self.cover_name):
                return True
        return False

    def _find_music_file(self, files):
        for any_file in files:
            for ext in self.music_exts:
                if any_file.endswith(ext):
                    return (any_file, ext)
        return (None, None)

    def _find_album_artist(self, directory, files):
        song_file, ext = self._find_music_file(files)
        if song_file is None:
            return (None, None)
        song = os.path.join(directory, song_file)
        if ext is 'flac':
            tags = FLAC(song)
            artist = tags['albumartist'][0]
            album = tags['album'][0]
        elif ext is 'mp3':
            tags = MP3(song)
            artist = tags['TPE2'].text[0]
            album = tags['TALB'].text[0]
        return (artist, album)

    def _get_album_art_url(self, artist, album):
        pic_url = self.itunes.find_art(artist, album)
        if not pic_url:
            pic_url = self.last_fm.find_art(artist, album)
        return pic_url

    def _save_pic(self, pic_url, directory):
        final_path = os.path.join(directory, self.cover_name + pic_url[-3:])
        f = urllib2.urlopen(pic_url)
        data = f.read()
        with open(final_path, 'wb+') as pic_data:
            pic_data.write(data)

    def find_albums(self):
        directory_walker = os.walk(self.root_directory)
        for directory, subdirectories, files in directory_walker:
            if len(files) == 0:
                continue
            if self._cover_already_exists(files):
                continue
            artist, album = self._find_album_artist(directory, files)
            if not artist or not album:
                continue
            pic_url = self._get_album_art_url(artist, album)
            if not pic_url:
                print 'Coulnd\'t find cover for ' + album + ' by ' + artist
            self._save_pic(pic_url, directory)
            print 'Found cover for ' + album + ' by ' + artist

if __name__ == '__main__':
    try:
        directory = sys.argv[1]
    except IndexError:
        directory = '.'
    grabber = AlbumArtGrabber(root_directory=directory)
    grabber.find_albums()
