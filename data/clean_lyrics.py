# Usage: python cleanlyrics.py <Directory>, where "Directory" is a subdirectory of the current
# working directory, and contains all of the folders of each of the artists needed, so each 
# artist's discography is a subdirectory of "Directory"

import os
import sys
import re

# Get path from the current directory and add the arg passed (assumes folder is in current directory)
path =  os.getcwd() + '/' + sys.argv[1] # [0] is this file, [1] is the parameter passed, keep global?

def label_contains_artist_name(label: str, artist: str) -> bool:
    pink_floyd_flag = (artist == "Pink Floyd") # Genius lists the singers of Pink Floyd in each label LOL
    if artist in label:
        return True
    elif pink_floyd_flag: # So check if any singers are in the labels for PF
        return (("Roger Waters" in label) or ("David Gilmour" in label) or ("Syd Barrett" in label)
                or ("Richard Wright" in label) or ("Nick Mason" in label))
    else: # At this point the artist isn't singing
        return False

if __name__ == "__main__":
    for this_dir, subdirs, files in os.walk(path): # Assumes the path only contains folders for each artist
        # this_dir is first the path directory, then iterates thru each artist, so it will be the artist's name
        # subdirs are the subdirectories of this_dir
        # files are the files of this_dir
        artist = this_dir[this_dir.rfind('/') + 1:] # Grab the name of the artist, rfind gets the last instance of...
        print(artist) # Print progress
        if this_dir == path:
            new_dir = this_dir + " Cleaned" # Create new cleaned dir for all artists
        else:
            new_dir = path + " Cleaned" + "/" + artist + " Cleaned" # Create new subdir for each artist
        os.mkdir(new_dir)
        for file in files: # for the set of files under this 
            with open(f"{this_dir}/{file}", 'r') as f:
                lyrics = f.readlines() # read into 'lyrics' var
                if lyrics: # if not NULL then erase the tag from the end of the lyrics
                    lyrics[-1] = re.sub(r'\d*[.]*\d*[K]*EmbedShare URLCopyEmbedCopy','', lyrics[-1])
                cleaned_lyrics = ""
                skipped_section = False # To check if it's still in a verse / chorus not sung by our artist
                for line in lyrics: # for each line in lyrics
                    if line[0] == '[': # for line that labels the next prose
                        #if only_song_part_label(line) or label_contains_artist_name(line, this_dir): # Useless
                        if ':' not in line: # Only a label, the singer is our artist
                            # Add to cleaned_lyrics and keep going in the for loop / adding to cleaned_lyrics
                            skipped_section = False # This section is sung by the artist, so include it
                            #cleaned_lyrics += line # SKIP this if we're taking out all labels
                        else: # A label with : means we must check for who is singing
                            if label_contains_artist_name(line, artist):
                                # The artist is singing, add this section to cleaned_lyrics
                                skipped_section = False
                                #cleaned_lyrics += line # SKIP this if we're taking out all labels
                            else: 
                                # Skip this part - don't add to cleaned_lyrics
                                skipped_section = True
                                continue # continue to next loop in this inner for loop
                    elif not skipped_section: # add line if it should be included
                        # This line is just lyrics, add to cleaned_lyrics
                        cleaned_lyrics += line
                f.close()
                try:
                    lyric_file = open(f"{new_dir}/{file}", "w") # Open new file and write lyrics
                    lyric_file.write(cleaned_lyrics)
                    lyric_file.close()
                except:
                    print(new_dir, file, "Something went wrong :(")

# Not used

# artist_names: set = {
#     "Eminem",
#     "Kanye West",
#     "Pink Floyd",
#     "Tame Impala",
#     "The Maine",
#     "The Story So Far"
# }

# def check_if_dir_exists(artist_name: str) -> bool:  
#     return artist_name in os.listdir()

# def convert_to_file_name(song_name: str) -> str:
#     song_name = song_name.strip()
#     file_name: str = ""

#     for c in song_name:
#         if c == " ":
#             file_name += "_"
#         elif c == "/":
#             file_name += "-"
#         else:
#             file_name += c
    
#     return file_name + ".txt"