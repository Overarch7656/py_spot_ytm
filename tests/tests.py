import unittest, os
from spotify import is_playlist_saved, make_safe_filename
from ytmusic import search_song

#TEST: make_safe_filename()
class TestUtils(unittest.TestCase):
    def test_safe_filename_removes_slashes(self):
        self.assertEqual(make_safe_filename("My/Playlist"), "My_Playlist")

    def test_safe_filename_removes_special_chars(self):
        self.assertEqual(make_safe_filename("Best Hits: 2022"), "Best Hits_ 2022")

    def test_safe_filename_preserves_good_chars(self):
        self.assertEqual(make_safe_filename("Classic_Hits-Vol.1"), "Classic_Hits-Vol.1")


#MOCK for YTMusic search
class MockYTMusic:
    def search(self, query, filter="songs"):
        if "exists" in query:
            return [{"videoId": "abc123"}]
        return []


#TEST: search_song() using mock YTMusic
class TestSearchSong(unittest.TestCase):
    def test_song_found(self):
        yt = MockYTMusic()
        vid = search_song(yt, "exists", "artist")
        self.assertEqual(vid, "abc123")

    def test_song_not_found(self):
        yt = MockYTMusic()
        vid = search_song(yt, "notfound", "artist")
        self.assertIsNone(vid)


#TEST: is_playlist_saved()
class TestPlaylistSaved(unittest.TestCase):
    def setUp(self):
        # Setup a fake playlist JSON file in the 'playlists/' folder
        self.playlist_name = "Test Playlist"
        self.safe_name = make_safe_filename(self.playlist_name)
        os.makedirs("playlists", exist_ok=True)
        self.path = f"playlists/{self.safe_name}.json"
        with open(self.path, "w") as f:
            f.write("[]")

    def tearDown(self):
        # Remove the test file after each test
        os.remove(self.path)

    # Test that is_playlist_saved returns True for existing playlist
    def test_is_playlist_saved_true(self):
        self.assertTrue(is_playlist_saved(self.playlist_name))

    # Test that is_playlist_saved returns False for non-existent playlist
    def test_is_playlist_saved_false(self):
        self.assertFalse(is_playlist_saved("Nonexistent Playlist"))

# TODO: Moke Spotify API for testing

if __name__ == '__main__':
    unittest.main()