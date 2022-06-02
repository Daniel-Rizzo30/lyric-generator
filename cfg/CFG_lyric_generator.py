# Daniel Rizzo
# CFG Lyric Generator
# Team: Ghazanfar Shahbaz, Chen Stanilovsky, Daniel Rizzo
# CSCI 49362 Natural Language Processing
# Professor Sarah Ita Levitan
# CFG_lyric_generator.py

# Usage: python CFG_lyric_generator.py <Directory>, where "Directory" is a subdirectory of the current
# working directory, and is the folder that contains all lyric files for the songs of the artist whose 
# name is the Directory
# Outputs to file named {artist}GeneratedLyrics.txt

# Post-Presentation Polishing: 
# Fixed the way punctuation is handled from the tokenizer - ignores all punct except apostrophes now
# Added unigram as last resort after trigram, bigram counts when selecting a new word

import os
import sys
import re # regex
import nltk # NLTK NLP library
import random
import math
from nltk import word_tokenize as tokenize
#from nltk import StanfordTagger as pos_tag2
from nltk.tag.stanford import StanfordPOSTagger as pos_tag # This version may work better

# Get path from the current directory and add the arg passed (assumes folder is in current directory)
path =  os.getcwd() + '/' + sys.argv[1] # [0] is this file, [1] is the parameter passed, keep global?

class POS:
    def __init__(self):
        self.information = [] # All parts of speech encountered (eg. NN VB)
        # this array will contain elements that will each have a part of speech and another array
        # which contains all words that were tagged with that pos and a count -> class WordPOS

class WordPOS:
    def __init__(self, word, count):
        self.word = word
        self.count = count     

if __name__ == "__main__":

    # pattern = r'''(?x)          # set flag to allow verbose regexps
    #         (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
    #       | \w+(?:-\w+)*        # words with optional internal hyphens
    #       | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
    #       | \.\.\.              # ellipsis
    #       | [][.,;"'?():_`-]    # these are separate tokens; includes ], [
    #       '''
    #tokenizer = nltk.RegexpTokenizer(r"\w+") # Tokenize words only, no punctuation
    
    # Tokenize words only, no punctuation except apostrophes - need both ' and ’ types...
    tokenizer = nltk.RegexpTokenizer(r"\w+[']\w+|\w+[’]\w+|\w+") 
    # Build the CFG from all songs and lyrics: 
    for this_dir, subdirs, files in os.walk(path): # Assumes the path only contains folders for each artist
        # this_dir is first the path directory, then iterates thru each artist, so it will be the artist's name
        # subdirs are the subdirectories of this_dir
        # files are the files of this_dir
        song_lengths_raw = [] # Store num of lines of each song in array
        word_lengths_raw = [] # ... number of words in each song
        artist = sys.argv[1] # Grab the name of the artist
        
        if (artist[-1] == '/'):
            artist = artist[0:-1] # Cut off the / so it is not used as a directory
        total_lines = 0
        print(artist) # Testing
        this_artist_pos = POS()
        bigrams = POS()
        trigrams = POS()
        skipgrams = POS()
        unigrams = POS()
        this_artist_rules = POS()

        for file in files: # for the set of files under this directory
            with open(f"{this_dir}/{file}", 'r') as readfile:
                print(file) # Testing
                num_lines = 0
                num_words_in_song = 0
                lyrics = readfile.readlines() # read into 'lyrics' var
                for line_raw in lyrics: # for each line in lyrics
                    if (not line_raw): # if empty
                        continue # go to next lyric line
                    line = tokenizer.tokenize(line_raw) # tokenize the lyrics, keeps all punctuation
                    #line = line_raw.split() # Try a different tokenization method
                    #line = nltk.regexp_tokenize(line_raw,pattern)
                    # Change m -> am s -> is, t -> not, ain -> am, won -> will, doesn -> does
                    # for i in range(len(line)):
                    #     if line[i] == 'm':
                    #         line[i] = 'am'
                    #     elif line[i] == 's':
                    #         line[i] = 'is'
                    #     elif line[i] == 't':
                    #         line[i] = 'not'
                    #     elif line[i] == 'ain':
                    #         line[i] = 'am'
                    #     elif line[i] == 'won' or line[i] == 'll':
                    #         line[i] = 'will'
                    #     elif line[i] == 'doesn':
                    #         line[i] = 'does'
                    #     elif line[i] == 've':
                    #         line[i] = 'have'
                    #     elif line[i] == 'don':
                    #         line[i] = 'do'
                    #     elif line[i] == 're':
                    #         line[i] = 'are'
                    #     elif line[i] == 'd':
                    #         line[i] = 'did'
                    num_words_in_song += len(line) # Add to word count total
                    pos_line_tuples = nltk.pos_tag(line) # get parts of speech, but it's in tuples, not list
                    # stores the line in an array of 2-tuples: (word, word_class)
                    line_tags = ''
                    pos_line = []
                    for i in range(len(pos_line_tuples)):
                        element = []
                        if (pos_line_tuples[i][1] != 'NN' and pos_line_tuples[i][1] != 'PRP' 
                            and pos_line_tuples[i][1] != 'NNP'): # Addressing capitalization
                            element.append(pos_line_tuples[i][0].lower()) # make it all lowercase
                        else:    
                            element.append(pos_line_tuples[i][0]) # do not lower() nouns - could be names
                        element.append(pos_line_tuples[i][1])
                        pos_line.append(element)
                    i = 0
                    #print(pos_line) # Testing
                    for i in range(len(pos_line)):  
                        word = pos_line[i][0]
                        word_class = pos_line[i][1]
                        if (not word_class): # if word couldn't be tagged
                            word_class = "UNK"
                        # Build the POS tagged sentence from this line
                        if (line_tags == ''):
                            line_tags = word_class
                        else:
                            line_tags = line_tags + " " + word_class

                        # Add word_class and word to information array
                        if (this_artist_pos.information == []):
                            wordarray = []
                            wordarray.append(WordPOS(word, 1))
                            element = [word_class, 1, wordarray]
                            this_artist_pos.information.append(element)
                        else:
                            class_flag = 0
                            word_flag = 0
                            # for xclass,totalcount,array in this_artist_pos.information:
                            for k in range(len(this_artist_pos.information)): 
                                if (this_artist_pos.information[k][0] == word_class): # class
                                    class_flag = 1 # this pos alrdy exists
                                    for j in range(len(this_artist_pos.information[k][2])):
                                        if (this_artist_pos.information[k][2][j].word == word): 
                                            word_flag = 1 # this word alrdy exists with the pos
                                            this_artist_pos.information[k][2][j].count += 1 # add to total count
                                    if (word_flag == 0): # append this word to this pos
                                        this_artist_pos.information[k][2].append(WordPOS(word, 1)) # append array
                                        this_artist_pos.information[k][1] += 1
                            if (class_flag == 0): # append this class to the information array
                                wordarray = []
                                wordarray.append(WordPOS(word, 1))
                                element = [word_class, 1, wordarray]
                                this_artist_pos.information.append(element)
                        
                        # Compute bigram counts
                        if (i <= len(pos_line) - 2):
                            next_word_class = pos_line[i + 1][1] # the next word's pos
                            next_word = pos_line[i + 1][0] # the next word
                            #print("Counting bigrams", next_word_class, next_word, i) # Testing
                            if (bigrams.information == []):
                                classarray = []
                                # Append to part of the element which will contain the next word's class 
                                # and an array of what words have come with that class
                                classarray.append([next_word_class, 1, [WordPOS(next_word, 1)]])
                                # this word along with all the classes that have come along after the word
                                element = [word, word_class, classarray] 
                                bigrams.information.append(element)
                            else: 
                                class_flag = 0
                                word1_flag = 0
                                word2_flag = 0
                                # for xword,xwordclass,array in bigrams.information: 
                                for z in range(len(bigrams.information)):
                                    if (bigrams.information[z][0] == word and bigrams.information[z][1] == word_class): 
                                        word1_flag = 1 # this word alrdy exists
                                        # for xclass,total_count,count_array in array: 
                                        for a in range(len(bigrams.information[z][2])): # accompanying array
                                            if (bigrams.information[z][2][0] == next_word_class): 
                                                class_flag = 1 # this class alrdy exists with the word
                                                bigrams.information[z][2][1] += 1 # inc. count
                                                #print(count_array) # Testing
                                                for x in range(len(bigrams.information[z][2][2])):
                                                    if bigrams.information[z][2][2][x].word == next_word:
                                                        word2_flag = 1
                                                        # Add one to this word's count
                                                        bigrams.information[z][2][2][x].count += 1
                                                if word2_flag == 0: # Add word to count_array
                                                    bigrams.information[z][2][2].append(WordPOS(next_word, 1))
                                                break
                                        if (class_flag == 0): # append this class to this word
                                            bigrams.information[z][2].append([next_word_class, 1, 
                                                [WordPOS(next_word, 1)]])
                                if (word1_flag == 0): # append this class to the information array
                                    classarray = []
                                    # Append to part of the element which will contain the next word's class 
                                    # and an array of what words have come with that class
                                    classarray.append([next_word_class, 1, [WordPOS(next_word, 1)]])
                                    # this word along with all the classes that have come along after the word
                                    element = [word, word_class, classarray] 
                                    bigrams.information.append(element)
                        
                        # Compute skip-trigram counts
                        if (i <= len(pos_line) - 3):
                            next_word_class = pos_line[i + 2][1] # the next word's pos
                            next_word = pos_line[i + 2][0] # the next word
                            #print("Counting bigrams", next_word_class, next_word, i) # Testing
                            if (skipgrams.information == []):
                                classarray = []
                                # Append to part of the element which will contain the next word's class 
                                # and an array of what words have come with that class
                                classarray.append([next_word_class, 1, [WordPOS(next_word, 1)]])
                                # this word along with all the classes that have come along after the word
                                element = [word, word_class, classarray] 
                                skipgrams.information.append(element)
                            else: 
                                class_flag = 0
                                word1_flag = 0
                                word2_flag = 0
                                # for xword,xwordclass,array in skipgrams.information: 
                                for z in range(len(skipgrams.information)):
                                    if (skipgrams.information[z][0] == word and 
                                        skipgrams.information[z][1] == word_class): 
                                        word1_flag = 1 # this word alrdy exists
                                        # for xclass,total_count,count_array in array: 
                                        for a in range(len(skipgrams.information[z][2])): # accompanying array
                                            if (skipgrams.information[z][2][0] == next_word_class): 
                                                class_flag = 1 # this class alrdy exists with the word
                                                skipgrams.information[z][2][1] += 1 # inc. count
                                                #print(count_array) # Testing
                                                for x in range(len(skipgrams.information[z][2][2])):
                                                    if skipgrams.information[z][2][2][x].word == next_word:
                                                        word2_flag = 1
                                                        # Add one to this word's count
                                                        skipgrams.information[z][2][2][x].count += 1
                                                if word2_flag == 0: # Add word to count_array
                                                    skipgrams.information[z][2][2].append(WordPOS(next_word, 1))
                                                break
                                        if (class_flag == 0): # append this class to this word
                                            skipgrams.information[z][2].append([next_word_class, 
                                                1, [WordPOS(next_word, 1)]])
                                if (word1_flag == 0): # append this class to the information array
                                    classarray = []
                                    # Append to part of the element which will contain the next word's class 
                                    # and an array of what words have come with that class
                                    classarray.append([next_word_class, 1, [WordPOS(next_word, 1)]])
                                    # this word along with all the classes that have come along after the word
                                    element = [word, word_class, classarray]
                                    skipgrams.information.append(element)

                        # Compute trigram counts fully
                        if (i <= len(pos_line) - 3):
                            third_word_class = pos_line[i + 2][1]
                            third_word = pos_line[i + 2][0]
                            next_word_class = pos_line[i + 1][1] # the next word's pos
                            next_word = pos_line[i + 1][0] # the next word
                            #print("Counting bigrams", next_word_class, next_word, i) # Testing
                            if (trigrams.information == []):
                                classarray = []
                                # Append to part of the element which will contain the next word's class 
                                # and an array of what words have come with that class
                                classarray.append([next_word_class, third_word_class, 1, 
                                    [WordPOS(next_word, 1)], [WordPOS(third_word, 1)]])
                                # this word along with all the classes that have come along after the word
                                element = [word, word_class, classarray]
                                trigrams.information.append(element)
                            else: 
                                class_flag = 0
                                word1_flag = 0
                                word2_flag = 0
                                # for xword,xwordclass,array in trigrams.information: 
                                for z in range(len(trigrams.information)):
                                    if (trigrams.information[z][0] == word and trigrams.information[z][1] == word_class): 
                                        word1_flag = 1 # this word alrdy exists
                                        # for xclass,total_count,count_array in array: 
                                        for a in range(len(trigrams.information[z][2])): # accompanying array
                                            if (trigrams.information[z][2][0] == next_word_class 
                                                and trigrams.information[z][2][1] == third_word_class): 
                                                class_flag = 1 # this class alrdy exists with the word
                                                trigrams.information[z][2][2] += 1 # inc. count
                                                #print(count_array) # Testing
                                                for x in range(len(trigrams.information[z][2][3])):
                                                    if ((trigrams.information[z][2][3][x].word == next_word) 
                                                        and (trigrams.information[z][2][4][x].word == third_word)):
                                                        word2_flag = 1
                                                        # Add one to these words' counts
                                                        trigrams.information[z][2][3][x].count += 1
                                                        trigrams.information[z][2][4][x].count += 1
                                                if word2_flag == 0: # Add word to count_array
                                                    trigrams.information[z][2][3].append(WordPOS(next_word, 1))
                                                    trigrams.information[z][2][4].append(WordPOS(third_word, 1))
                                                break
                                        if (class_flag == 0): # append this class to this word
                                            trigrams.information[z][2].append([next_word_class, 
                                                third_word_class, 1, [WordPOS(next_word, 1)], 
                                                [WordPOS(third_word, 1)]]) # append array
                                if (word1_flag == 0): # append this class to the information array
                                    classarray = []
                                    # Append to part of the element which will contain the next word's class 
                                    # and an array of what words have come with that class
                                    classarray.append([next_word_class, third_word_class, 1, 
                                    [WordPOS(next_word, 1)], [WordPOS(third_word, 1)]])
                                    # this word along with all the classes that have come along after the word
                                    element = [word, word_class, classarray] 
                                    trigrams.information.append(element)

                        # Compute unigram counts
                        #print("Counting unigrams", word, word_class, i) # Testing
                        if (unigrams.information == []):
                            classarray = []
                            # Append to part of the element which will contain the next word's class 
                            # and an array of what words have come with that class
                            classarray.append([word, 1])
                            # this word along with all the classes that have come along after the word
                            element = [word_class, classarray] 
                            unigrams.information.append(element)
                        else: 
                            class_flag = 0
                            word_flag = 0
                            # for xwordclass,array in unigrams.information: 
                            for z in range(len(unigrams.information)):
                                if (unigrams.information[z][0] == word_class): 
                                    class_flag = 1 # this class alrdy exists
                                    for a in range(len(unigrams.information[z][1])): # accompanying array
                                        if (unigrams.information[z][1][a][0] == word): 
                                            word_flag = 1 # this word alrdy exists within the classs
                                            unigrams.information[z][1][a][1] += 1 # inc. count
                                            break
                                    if (word_flag == 0): # append this class to this word
                                        unigrams.information[z][1].append([word, 1]) # append array
                            if (class_flag == 0): # append this class to the information array
                                classarray = []
                                # Append to part of the element which will contain the next word's class 
                                # and an array of what words have come with that class
                                classarray.append([word, 1])
                                # this word along with all the classes that have come along after the word
                                element = [word_class, classarray]
                                unigrams.information.append(element)


                    # Add fully tagged lyric to an array of pos tags and their counts
                    if (this_artist_rules.information == [] and line_tags): # if tag is non empty
                        this_artist_rules.information.append([line_tags, 1])
                        num_lines += 1 # only add to statistics when lines are added
                        total_lines += 1
                    else: 
                        tag_flag = 0
                        # for rule,count in this_artist_rules.information:
                        for b in range(len(this_artist_rules.information)):
                            if (this_artist_rules.information[b][0] == line_tags): # this rule is already in the array
                                tag_flag = 1
                                this_artist_rules.information[b][1] += 1 # just increment count
                                num_lines += 1 # only add to statistics when lines are added
                                total_lines += 1
                                break # Stop computing
                        if (tag_flag == 0 and line_tags): # if tag is non empty
                            this_artist_rules.information.append([line_tags, 1]) # not in array yet, so add whole element
                            num_lines += 1 # only add to statistics when lines are added
                            total_lines += 1
                
                word_lengths_raw.append(num_words_in_song) # add total words to array
                song_lengths_raw.append(num_lines) # add num lines to array
                    
        # All songs are done
        # Compute ranges and stats for word_lengths_raw
        max_word_length = max(word_lengths_raw)
        min_word_length = min(word_lengths_raw)

        song_document = []
        number_of_lines = 0
        generated_word_count = 0 # Count how many words will be in this song
        i = 0
        while number_of_lines == 0: # Songs that have no lyrics can give 0 lines to this process
            u = random.uniform(0,1) # Pick the number of lines randomly
            line_index = math.floor(len(song_lengths_raw) * u)
            number_of_lines = song_lengths_raw[line_index] # Obtain num of lines from that index
        while (i < number_of_lines) or (generated_word_count < min_word_length): # For each line to fill
            generated_line = []
            sum = 0
            cfg_rule = 'null'
            u = random.uniform(0,1) # Pick the CFG rule randomly
            #print(u) # Testing
            #print(total_lines) # Testing
            for j in range(len(this_artist_rules.information)):
                #print(sum) # Testing
                #print(this_artist_rules.information[j][1]) # Testing
                sum += this_artist_rules.information[j][1]
                if (u < (sum / total_lines)):
                    cfg_rule = this_artist_rules.information[j][0] # Choose this index's rule
                    break # Stop computing, skip looping
            #print(sum, "is sum") # Testing
            cfg_rule = re.split('\s+', cfg_rule)
            #print(cfg_rule) # Testing
            for k in range(len(cfg_rule)): # For each pos tag in the chosen rule
                # Choose words
                word_chosen = ''
                
                if k > 1 and word_chosen == '': # Choose word off of full trigram
                    previous_word_chosen = generated_line[k - 2]
                    previous_word_class = cfg_rule[k - 2]
                    middle_word_chosen = generated_line[k - 1]
                    middle_word_class = cfg_rule[k - 1]
                    max_trigram_count = -1
                    max_trigram_index = -1
                    l = 0
                    m = 0
                    z = 0
                    #for xword,xwordclass,array in trigrams.information: 
                    for l in range(len(trigrams.information)):
                        if (trigrams.information[l][0] == previous_word_chosen and 
                            trigrams.information[l][1] == previous_word_class):
                            #print("Trigram") # Testing
                            #for xclass,total_count,count_array in trigrams.information[l][2]: 
                            for m in range(len(trigrams.information[l][2])):
                                # If this is the classes being looked for
                                if (trigrams.information[l][2][m][1] == cfg_rule[k] 
                                    and trigrams.information[l][2][m][0] == cfg_rule[k - 1]): 
                                    # for z,wordpos in enumerate(count_array):
                                    # find the most likely word choice
                                    for z in range(len(trigrams.information[l][2][m][4])): 
                                        wordpos = trigrams.information[l][2][m][4][z]
                                        if wordpos.count > max_trigram_count:
                                            max_trigram_index = z
                                            max_trigram_count = wordpos.count
                                    if (max_trigram_index != -1):
                                        # Set the most likely word
                                        word_chosen = trigrams.information[l][2][m][4][max_trigram_index].word 
                                        #print("Found Trigram Word", word_chosen) # Testing
                                        break

                if k > 0 and word_chosen == '': # Choose all words based off of bigrams from prev word
                    previous_word_chosen = generated_line[k - 1]
                    previous_word_class = cfg_rule[k - 1]
                    max_bigram_count = -1
                    max_bigram_index = -1
                    l = 0
                    m = 0
                    z = 0
                    #for xword,xwordclass,array in bigrams.information: 
                    for l in range(len(bigrams.information)):
                        if (bigrams.information[l][0] == previous_word_chosen and 
                            bigrams.information[l][1] == previous_word_class):
                            #print("Bigram") # Testing
                            #for xclass,total_count,count_array in bigrams.information[l][2]: 
                            for m in range(len(bigrams.information[l][2])):
                                # If this is the class being looked for
                                if (bigrams.information[l][2][m][0] == cfg_rule[k]): 
                                    # for z,wordpos in enumerate(count_array):
                                    # find the most likely word choice
                                    for z in range(len(bigrams.information[l][2][m][2])): 
                                        wordpos = bigrams.information[l][2][m][2][z]
                                        if wordpos.count > max_bigram_count:
                                            max_bigram_index = z
                                            max_bigram_count = wordpos.count
                                    if (max_bigram_index != -1):
                                        # Set the most likely word
                                        word_chosen = bigrams.information[l][2][m][2][max_bigram_index].word 
                                        #print("Found Bigram Word", word_chosen) # Testing
                                        break
                
                if k > 1 and word_chosen == '': # Choose word off of skip-trigram if not chosen yet
                    previous_word_chosen = generated_line[k - 2]
                    previous_word_class = cfg_rule[k - 2]
                    max_skipgram_count = -1
                    max_skipgram_index = -1
                    l = 0
                    m = 0
                    z = 0
                    #for xword,xwordclass,array in skipgrams.information: 
                    for l in range(len(skipgrams.information)):
                        if (skipgrams.information[l][0] == previous_word_chosen and 
                            skipgrams.information[l][1] == previous_word_class):
                            #print("Skipgram") # Testing
                            #for xclass,total_count,count_array in skipgrams.information[l][2]: 
                            for m in range(len(skipgrams.information[l][2])):
                                # If this is the class being looked for
                                if (skipgrams.information[l][2][m][0] == cfg_rule[k]): 
                                    # for z,wordpos in enumerate(count_array):
                                    # find the most likely word choice
                                    for z in range(len(skipgrams.information[l][2][m][2])): 
                                        wordpos = skipgrams.information[l][2][m][2][z]
                                        if wordpos.count > max_skipgram_count:
                                            max_skipgram_index = z
                                            max_skipgram_count = wordpos.count
                                    if (max_skipgram_index != -1):
                                        # Set the most likely word
                                        word_chosen = skipgrams.information[l][2][m][2][max_skipgram_index].word 
                                        #print("Found Skipgram Word", word_chosen) # Testing
                                        break
                
                if word_chosen == '' and k > 0: # If still blank, use unigram count # k > 0 ?
                        for l in range(len(unigrams.information)):
                            if (unigrams.information[l][0] == cfg_rule[k]):
                                #print("Unigram") # Testing
                                max_unigram_count = -1
                                max_unigram_index = -1
                                for m in range(len(unigrams.information[l][1])):
                                    if (unigrams.information[l][1][m][1] > max_unigram_count):
                                        max_unigram_index = m
                                        max_unigram_count = unigrams.information[l][1][m][1]
                                if (max_unigram_index != -1):
                                        # Set the most likely word
                                        word_chosen = unigrams.information[l][1][max_unigram_index][0] 
                                        #print("Found Skipgram Word", word_chosen) # Testing
                                        break

                # If not in trigram, skip-trigram, bigram and unigram, or if first word then choose randomly from its tag
                if k == 0 or word_chosen == '': # Change to IF to stop testing bigrams
                    for z in range(len(this_artist_pos.information)):
                        if (this_artist_pos.information[z][0] == cfg_rule[k]):
                            sum = 0
                            u = random.uniform(0,1) # Pick word randomly
                            for y in range(len(this_artist_pos.information[z][2])):
                                sum += this_artist_pos.information[z][2][y].count
                                if (u < sum / this_artist_pos.information[z][1]):
                                    word_chosen = this_artist_pos.information[z][2][y].word
                                    break
                            break # Stop computing, skip looping
                
                # Add word to this lyric line
                #print(word_chosen) # Testing
                generated_line.append(word_chosen)
                generated_word_count += 1

            # Add full lyric to song document
            generated_line[0] = generated_line[0].capitalize() # Capitalize first letter
            #print(generated_line) # Testing
            song_document.append(generated_line)
            i += 1
            if (generated_word_count > max_word_length): # Put an upper limit on the song length
                break

        # Output generated song document
        writefile = open(f"{artist}NewGeneratedLyrics.txt", 'w') # Open new file to write lyrics to
        for i in range(len(song_document)):
            for j in range(len(song_document[i])):
                writefile.write(song_document[i][j] + " ") # print word
            writefile.write("\n") # end line
        writefile.close()
        #print(song_document) # Testing