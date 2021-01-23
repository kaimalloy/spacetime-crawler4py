"""
    CS 121: Assignment 1 Part A.
"""
# fix the empty character thing when regex split.
# á, ê character tested.
# catches non existent files and non txt extensions.
# empty file checked.

import os
import sys
import re


def check_files(num_files):
    """ Read filename and check if right number of files. O(n): n being the number of files in command line argument."""
    if len(sys.argv) == num_files + 1:
        count = 0
        for f in sys.argv[1:]:
            if not os.path.exists(f) or not f.endswith('.txt'):
                print("File path '" + f + "' is invalid. Try again.")
            else:
                count += 1
        if count == num_files:
            return sys.argv[1:]
    else:
        print('Include right number of file paths in command line arguments.')

def read_chunks(file_obj, size=1024):
    """ Read chunks from the file. O(n): n being the number of chunks of size.
        Reference: https://stackoverflow.com/questions/519633/lazy-method-for-reading-big-file-in-python """
    while True:
        piece = file_obj.read(size)
        if not piece:
            break
        yield piece.lower()

def tokenize(piece):
    """ Split into tokens with regex. Regex split is O(n): n being every character since it scans through. """
    return re.split('[^a-z0-9]+', piece)


def compute_word_frequencies(freq_dict, words):
    """ Add in words to dictionary frequencies. O(n): n being the word tokens since dict.get() is O(1). """
    for w in words:
        freq_dict[w] = freq_dict.get(w, 0) + 1


def print_frequencies(freq_dict, top=0):
    """ Print frequencies dictionary. O(nlogn): n being the dict items. sort first then for loop so O(nlogn) + O(n) = O(nlogn)
        Big-O Reference: https://stackoverflow.com/questions/14434490/what-is-the-complexity-of-this-python-sort-method"""
    count = 0
    for k,v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True):
        print(f'{k} -> {v}')
        count += 1
        if top and count == top:  # option to only print the first few
            break

def read_file(_file, prnt=True, prnt_top=0, size=1024):
    """Reads file chunk by chunk.

       O(nlogn):
                read_chunks O(n): n is every chunk
                    tokenize O(n): n is each character in chunk
                    compute_word_frequencies O(n): n is each word from tokenize
                = O(n) because it cycles through each character in the file once
                +
                del O(1)
                +
                print_frequencies O(nlogn): because of sorted()
                = O(n) + O(1) + O(nlogn) = O(nlogn)
       """
    freq_dict = {} # used to store the frequencies
    with open(_file) as f:
        for chunk in read_chunks(f, size):
            words = tokenize(chunk)
            compute_word_frequencies(freq_dict, words)
    
    if "" in freq_dict:
        del freq_dict[""] # remove empty string
    
    if prnt:
        print_frequencies(freq_dict, prnt_top)

    return freq_dict

def part_a(prnt=True, prnt_top=0, size=1024):
    """ Function to run part A of Assignment 1.

        FINAL O(nlogn):
                check_files O(n): n being the number of command line files
                +
                read_file O(nlogn): n being the words in the file (sorted)
                = O(nlogn)
       """
    file_obj = check_files(1)

    if file_obj:  # continue if no errors
        return read_file(file_obj[0], prnt, prnt_top, size)

if __name__ == "__main__":
    # part_a(prnt_top=15) # print first 15
    part_a()
