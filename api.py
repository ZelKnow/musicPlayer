import os
import sys
import json
import base64
import binascii
from Crypto.Cipher import AES
import requests
from requests.exceptions import RequestException, Timeout, ProxyError
from requests.exceptions import ConnectionError as ConnectionException
from http import cookiejar as cookielib

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pub_key = '010001'

class SearchNotFound(RequestException):
    """Search api return None."""

class SongNotAvailable(RequestException):
    """Some songs are not available, for example Taylor Swift's songs."""

class Song(object):

    def __init__(self, song_id, song_name, artist_id=None, artist_name=None, 
                 album_id=None, album_name=None, pop=None, song_lyric=None,
                 song_url=None):
        self.song_id = song_id
        self.song_name = song_name
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.album_id = album_id
        self.album_name = album_name
        self.pop = pop
        self.song_lyric = '' if song_lyric is None else song_lyric
        self.song_url = '' if song_url is None else song_url

class Album(object):

    def __init__(self, album_id, album_name, artist_id=None, artist_name=None):
        self.album_id = album_id
        self.album_name = album_name
        self.artist_id = artist_id
        self.artist_name = artist_name

def exception_handle(method):
    """Handle exception raised by requests library."""

    def wrapper(*args, **kwargs):
        try:
            result = method(*args, **kwargs)
            return result
        except ProxyError:
            LOG.exception('ProxyError when try to get %s.', args)
            raise ProxyError('A proxy error occurred.')
        except ConnectionException:
            LOG.exception('ConnectionError when try to get %s.', args)
            raise ConnectionException('DNS failure, refused connection, etc.')
        except Timeout:
            LOG.exception('Timeout when try to get %s', args)
            raise Timeout('The request timed out.')
        except RequestException:
            LOG.exception('RequestException when try to get %s.', args)
            raise RequestException('Please check out your network.')

    return wrapper


#不太懂
def encrypted_request(text):
    text = json.dumps(text)
    sec_key = create_secret_key(16)
    enc_text = aes_encrypt(aes_encrypt(text, nonce), sec_key.decode('utf-8'))
    enc_sec_key = rsa_encrpt(sec_key, pub_key, modulus)
    data = {'params': enc_text, 'encSecKey': enc_sec_key}
    return data

def aes_encrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(secKey.encode('utf-8'), AES.MODE_CBC, b'0102030405060708')
    ciphertext = encryptor.encrypt(text.encode('utf-8'))
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext

def rsa_encrpt(text, pubKey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)

def create_secret_key(size):
    return binascii.hexlify(os.urandom(size))[:16]



class Crawler(object):
    """NetEase Music API."""

    def __init__(self, timeout=60, proxy=None):
        self.session = requests.Session()
        self.timeout = timeout
        self.proxies = {'http': proxy, 'https': proxy}

    @exception_handle
    def post_request(self, url, params):
        """Send a post request.

        :return: a dict or raise Exception.
        """

        data = encrypted_request(params)
        resp = self.session.post(url, data=data, timeout=self.timeout,
                                 proxies=self.proxies)

        result = resp.json()
        if result['code'] != 200:
            LOG.error('Return %s when try to post %s => %s',
                      result, url, params)
            raise PostRequestIllegal(result)
        else:
            return result

    def get_request(self, url):
        """Send a get request.

        warning: old api.
        :return: a dict or raise Exception.
        """

        resp = self.session.get(url, timeout=self.timeout,
                                proxies=self.proxies)
        result = resp.json()
        if result['code'] != 200:
            LOG.error('Return %s when try to get %s', result, url)
            raise GetRequestIllegal(result)
        else:
            return result



    def search(self, search_content, search_type=1, limit=100):
        """Search entrance.

        :params search_content: search content.
        :params search_type: search type.
        :params limit: result count returned by weapi.
        :return: a dict.
        """

        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        params = {'s': search_content, 'type': search_type, 'offset': 0,
                  'sub': 'false', 'limit': limit}
        result = self.post_request(url, params)
        return result['result']

    def search_song(self, song_name, quiet=False, limit=100):
        """Search song by song name.

        :params song_name: song name.
        :params quiet: automatically select the best one.
        :params limit: song count returned by weapi.
        :return: a Song object.
        """

        post_result = self.search(song_name, search_type=1, limit=limit)

        if 'msg' in post_result.keys() or post_result['result']['songCount'] <= 0:
            raise SearchNotFound('Song {} not existed.'.format(song_name))
        else:
            songs = post_result['result']['songs']
            if quiet:
                song_id, song_name = songs[0]['id'], songs[0]['name']
                song = Song(song_id, song_name)
                return song
            else:
                result = []
                for i in range(len(songs)):
                    song_id = songs[i]['id']
                    song_name = songs[i]['name']
                    artist_id = songs[i]['ar'][0]['id']
                    artist_name = songs[i]['ar'][0]['name']
                    album_id = songs[i]['al']['id']
                    album_name = songs[i]['al']['name']
                    pop = songs[i]['pop']
                    song = Song(song_id, song_name, artist_id, artist_name, album_id, album_name, pop)
                    result.append(song)
                return result


    def get_song_url(self, song_id, bit_rate=320000):
        """Get a song's download address.

        :params song_id: song id<int>.
        :params bit_rate: {'MD 128k': 128000, 'HD 320k': 320000}
        :return: a song's download address.
        """
        url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(song_id)
        return url

    def get_song_lyric(self, song_id):
        """Get a song's lyric.

        warning: use old api.
        :params song_id: song id.
        :return: a song's lyric.
        """

        url = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(  # NOQA
            song_id)
        result = self.get_request(url)
        if 'lrc' in result and result['lrc']['lyric'] is not None:
            lyric_info = result['lrc']['lyric']
        else:
            lyric_info = 'Lyric not found.'
        return lyric_info

    def search_album(self, album_name, limit=9):
        """Search album by album name.

        :params album_name: album name.
        :params quiet: automatically select the best one.
        :params limit: album count returned by weapi.
        :return: a Album object.
        """

        post_result = self.search(album_name, search_type=10, limit=limit)
        albums = post_result['result']['albums']
        result = []
        for i in range(len(albums)):
            album_id = albums[i]['id']
            album_name = albums[i]['name']
            artist_id = albums[i]['artist']['id']
            artist_name = albums[i]['artist']['name']
            album = Album(album_id, album_name, artist_id, artist_name)
            result.append(album)
        return result
    '''
    def get_album_songs(self, album_id):
        """Get a album's all songs.

        warning: use old api.
        :params album_id: album id.
        :return: a list of Song object.
        """

        url = 'http://music.163.com/api/album/{}/'.format(album_id)
        result = self.get_request(url)

        songs = result['album']['songs']
        result = []
        for i in range(len(songs)):
            song_id = songs[i]['id']
            song_name = songs[i]['name']
            artist_id = songs[i]['ar'][0]['id']
            artist_name = songs[i]['ar'][0]['name']
            album_id = songs[i]['al']['id']
            album_name = songs[i]['al']['name']
            pop = songs[i]['pop']
            song = Song(song_id, song_name, artist_id, artist_name, album_id, album_name, pop)
            result.append(song)
        return result
        '''


netease = Crawler()

if __name__ == '__main__':
    a = Crawler()
    res = a.search('周杰伦')
    id = res['songs'][0]['id']
    print(a.get_song_url(id))