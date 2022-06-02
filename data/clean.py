from typing import List, Dict
import multiprocessing 
import itertools
import os 
import string

def get_all_song_paths() -> Dict[str, set]:
    artists: Dict[str, List[str]] = {}

    for path in os.listdir():
        if os.path.isdir(path):
            if path in artists.keys():
                artists[path] = set()

            artists[path] = set(os.listdir(path))
    
    return artists 

artists: Dict[str, set] = get_all_song_paths()     
cleaned_summary: dict = {
    "Edited Files": set(),
    "Deleted Files": set()
}
bands: set = {"Pink Floyd", "The Maine", "The Story So Far" }

def song_name_without_parens(song_name: str) -> str:
    name: str = ""
    in_parens: bool = False 

    for c in song_name:
        if not in_parens and c != "(":
            name += c 
        elif c == "(":
            if name and name[-1] == "_":
                name = name[:len(name) - 1]

            in_parens = True 
        elif c == ")":
            in_parens = False 

    return name 

def clean_inside_brackets(line: str) -> str:
    string_inside_brackets: str = ""
    
    for c in line:
        if c.isalpha() or c == " ":
            string_inside_brackets += c 
    
    return string_inside_brackets.strip()


def process_line(line: str) -> str:
    cleaned_line: str = ""

    for c in line:
        if c.isalpha() or c == " " or c in string.punctuation:
            cleaned_line += c.lower()

    return cleaned_line


def clean_song(data) -> None:
    artist, song_name = data[0], data[1]
    if "edited_" == song_name[:7]:
        return

    song_path: str = f"{artist}/{song_name}"
    cleaned_song_name: str = song_name_without_parens(song_name)

    global artists
    if cleaned_song_name != song_name and cleaned_song_name in artists[artist]:
        os.remove(song_path)
        global cleaned_summary
        cleaned_summary["Deleted Files"].add(song_path)
        return

    cleaned_song: str = ""
    File = open(song_path, "r")
    not_artist_lines:bool = False

    for line in File:
        line = line.strip()
        if not line: 
            cleaned_song += "\n"
            continue 

        if line[0] == "[":
            string_inside_brackets: str = clean_inside_brackets(line)

            if not (string_inside_brackets in ["Verse", "Intro", "Chorus", "Bridge"] or artist in string_inside_brackets or  "Part" in string_inside_brackets or artist in bands):
                not_artist_lines = True 
            else:
                not_artist_lines = False


            continue 

        if not not_artist_lines:
            cleaned_song += process_line(line) + "\n"

    File.close()

    cleaned_song = cleaned_song.rstrip()
    print(cleaned_song[len(cleaned_song) -27:])
    if cleaned_song[len(cleaned_song) -27:].lower() == "EmbedShare URLCopyEmbedCopy".lower():
        remove_length: int = 27
        index:int = len(cleaned_song) -28

        while not cleaned_song[index].isalpha():
            index -= 1 
            remove_length += 1

        cleaned_song = cleaned_song[:len(cleaned_song) - remove_length]


 
    os.makedirs(f"edited_{artist}", exist_ok=True)

    cleaned_file = open(f"edited_{artist}/{song_name}", "w")
    cleaned_file.write(cleaned_song)
    cleaned_file.close()




def clean_artist_songs(artist: str):
    core_count: int = 20

    with multiprocessing.Pool(core_count) as processor:
        processor.map(clean_song, zip(itertools.repeat(artist), artists[artist]))

if __name__ == '__main__':

    for artist in artists.keys():
        clean_artist_songs(artist)
    

    print(cleaned_summary)