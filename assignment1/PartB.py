"""
    CS 121: Assignment 1 Part B.
"""

from PartA import check_files, read_file

def prnt_intersection(d1, d2):
    """ Calculates the intersection of two lists. O(min(len(d1.keys()), len(d2.keys()))): because intersection of sets
        Big-O reference: https://www.geeksforgeeks.org/internal-working-of-set-in-python/"""
    intersect = list(set(d1.keys()) & set(d2.keys()))
    print(len(intersect))
    # print(intersect)


def part_b(size=1024):
    """ Function to run part B of Assignment 1. 
    
        FINAL O(nlogn):
                check_files O(n): n being the number of command line files
                +
                read_file O(nlogn): n being the words in the first file (sorted)
                +
                read_file O(nlogn): n being the words in the second file (sorted)
                +
                prnt_intersection O(min(len(d1.keys()), len(d2.keys()))): which is roughly O(n)
                = O(n) + O(nlogn) + O(nlogn) + O(n) = O(nlogn)
       """
    file_obj = check_files(2)

    if file_obj:  # continue if no errors
        freq_dict1 = read_file(file_obj[0], prnt=False, size=size)
        freq_dict2 = read_file(file_obj[1], prnt=False, size=size)

        prnt_intersection(freq_dict1, freq_dict2)


if __name__ == "__main__":
    part_b()
