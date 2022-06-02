from lyricsgenius import Genius
from dotenv import load_dotenv, main
import lyricsgenius 
import multiprocessing 
import os

from itertools import repeat
from lyricsgenius.api.public_methods import artist


load_dotenv()
genius: Genius = Genius(os.environ["genius_access_token"])
genius.verbose =False 
threads_available=6 #  change this if to be below core count*2

artist_names: set = {
    "Eminem",
    "Kanye West",
    "Pink Floyd",
    "Tame Impala",
    "The Maine",
    "The Story So Far"
}


def check_if_dir_exists(artist_name: str) -> bool:  
    return artist_name in os.listdir()

def convert_to_file_name(song_name: str) -> str:
    song_name = song_name.strip()
    file_name: str = ""

    for c in song_name:
        if c == " ":
            file_name += "_"
        elif c == "/":
            file_name += "-"
        else:
            file_name += c
    
    return file_name + ".txt"

def save_lyrics(song: Genius.song) -> None:
    artist_name: str = song.artist
    file_name: str= convert_to_file_name(song.title)
    try:
        lyric_file = open(f"{artist_name}/{file_name}", "w")
        lyric_file.write(song.lyrics)
    except:
        print(artist_name, file_name, "Something went wrong :(")

def get_artist_songs(name: str, amount=150) -> None:
    if not check_if_dir_exists(name):
        os.mkdir(name)

    global genius
    try:
        songs = genius.search_artist(name, max_songs=amount, sort="popularity", include_features=False).songs

        for song in songs:
            save_lyrics(song)
    except:
        print("Something went wrong with", name)

    # dont feel like laerning celery, use the code if its only 1 artist, comment 
    # with multiprocessing.Pool(threads_available//len(artist_names)) as processor:
    #     processor.map(save_lyrics, songs)
    

if __name__ == "__main__":
    # make it faster by doing offset for page per core
    with multiprocessing.Pool(len(artist_names)) as processor:
        processor.map(get_artist_songs, artist_names)

