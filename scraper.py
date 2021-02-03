import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from tokenizer import PartA as tk
import os

stopwords = [
    'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very',
    'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most',
    'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until',
    'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself',
    'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no',
    'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves',
    'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you',
    'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't',
    'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'
]

# This is a list of the fingerprints of the websites visited
web_fingerprints = []

# This is a list of every url that has been visited
# Only the BASE url is saved.  The query parameters and fragments are cut off
urls_visited = []

# Track the largest webpage.
# This is a tuple where the first element is the website name
# and the second element is the number of words in the website (excluding stop words)
largest_webpage = ["", 0]

# This will pair each word with the number of times it has been found in the webpages crawled
words_found = {}


def scraper(url, resp, logger):
    links = extract_next_links(url, resp, logger)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, logger):
    # List of links to return
    links = list()

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        # Add the base version of this url to the list of urls visited
        urls_visited.append(url)

        # Build the soup of the HTML content
        soup = BeautifulSoup(resp.raw_response.content)

        # Tokenize the words in the soup and count them
        words = tk.tokenize(soup.get_text())
        words = [w for w in words if w not in stopwords]
        num_words = len(words)

        if 200 <= num_words < 90000:
            # Create the fingerprint of the website
            fingerprint = simhash(words)
            logger.info("SCRAPER - Generated fingerprint for url", url, ":", fingerprint)

            for fprint in web_fingerprints:
                # If this website is too similar to another website in the list,
                # return an empty list of links
                if bitwise_similarity(fingerprint, fprint) > 0.95:
                    web_fingerprints.append(fingerprint)
                    logger.info("SCRAPER - SKIPPED website", url,
                                "because it was too similar to a website that was already crawled")
                    return links

            logger.info("SCRAPER - SCRAPING website", url, " for the links")

            # Loop through the words and increment the times the word occurs
            for w in words:
                # If the word has already been found, increment it
                if w in words_found:
                    words_found[w] += 1
                # If this is the first time we found the word, set it to 1
                else:
                    words_found[w] = 1

            # Update the largest webpage found, if necessary
            if num_words > largest_webpage[1]:
                largest_webpage[0] = url
                largest_webpage[1] = num_words
                logger.info("SCRAPER - updating largest website to", url, "with", num_words, "words")

            # Append the fingerprint to the list
            web_fingerprints.append(fingerprint)

            # Append all links to the list of links to return
            for link in soup.find_all('a'):
                # Check to be sure the link has an href attribute
                if link.has_attr('href'):
                    # Cut query parameters and fragments out of the href attribute value
                    href = base_url(link.get('href'))

                    # Check to make sure this link has not been crawled already
                    if href not in urls_visited:
                        links.append(href)
        else:
            logger.info("SCRAPER - SKIPPED website", url, "because the website was either too big or too small")
    else:
        logger.info("SCRAPER - SKIPPED website", url, "because the server returned error code <" + resp.status + ">")

    return links


def is_valid(url):
    # List of valid hostnames
    valid_hostnames = [
        "ics.uci.edu",
        "cs.uci.edu",
        "informatics.uci.edu",
        "stat.uci.edu",
    ]

    try:
        parsed = urlparse(url)

        # Only allow http schemes
        if parsed.scheme not in {"http", "https"}:
            return False

        # Only allow urls that have valid hostname and path
        if not any([host in url for host in valid_hostnames]) and \
                "today.uci.edu/department/information_computer_sciences" not in url:
            return False

        # Remove non-webpage links
        # NOTE: this does not seem to be filtering out all pdfs
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|json|sql|ova|apk)$", parsed.path.lower())

    except TypeError:
        print("TypeError for", url)
        raise

# Given a list of strings, compute a 32 bit binary string that represents
# a "good enough" approximation of the words in the list
def simhash(tokens):
    weight_dict = tk.computeWordFrequencies(tokens)

    bin_dict = {}
    vector = [0 for i in range(32)]
    fingerprint = ""

    for key in weight_dict:
        # Add the binary version of the key to the dictionary
        bin_dict[key] = bin(hash(key))

        # Check if the word is too short
        if len(bin_dict[key]) < 32:
            # NOTE: this could be a problem - if too many binary strings have a bunch of zeroes appended to the end
            # then they might match as similar to another one that is not really that "similar"
            bin_dict[key] += "0" * 32

        # Take only 32 bits
        bin_dict[key] = bin_dict[key][0:32]

        # Replace negative and b with 0
        bin_dict[key] = bin_dict[key].replace('-', '0')
        bin_dict[key] = bin_dict[key].replace('b', '0')

    # Iterate over all the keys in the dictionary
    for key in weight_dict:
        # Iterate over all the bits in the binary strings
        for i in range(32):
            # Add the word's weight if the current bit is true, and subtract if it is false
            if bin_dict[key][i] is "1":
                vector[i] += weight_dict[key]
            else:
                vector[i] -= weight_dict[key]

    # Iterate over the vector.  For each positive number, add a 1 to the fingerprint, and each negative add a zero
    for i in range(32):
        if vector[i] > 0:
            fingerprint += '1'
        else:
            fingerprint += '0'

    return fingerprint


# Check how similar two strings are
def bitwise_similarity(bstr1, bstr2):
    if len(bstr1) != len(bstr2):
        return 0

    summation = 0
    for i in range(len(bstr1)):
        if bstr1[i] == bstr2[i]:
            summation += 1

    return summation / len(bstr1)


def base_url(url):
    # Remove parameters, queries, and fragments from the url
    url = list(urlparse(url))
    url[3] = url[4] = url[5] = ""
    url = urlunparse(url)

    # Make sure that none of the urls end with a slash
    if url.endswith("/"):
        return url.rstrip("/")

    return url


# Return a sorted list of tuples where the hostname is associated with the number of paths of that site visited
def compute_subdomain_visits(domain):
    # Dictionary pairs the hostname with the number of times that it was visited
    visits = {}

    # Append all unique hostnames to the list
    for url in urls_visited:
        parsed = urlparse(url)

        # Check if the desired domain is in the hostname of the current url
        if domain in parsed.hostname:
            # If the hostname is already in visits, increment the number
            if parsed.hostname in visits:
                visits[parsed.hostname] += 1
            # If the hostname is not in visits, this is the first appearance, so set it to 1
            else:
                visits[parsed.hostname] = 1

    # [ (acar.ics.uci.edu, 4) , (bell.ics.uci.edu, 6) ]
    return sorted(visits)

def final_report():
    f = open("report.txt", "w")

    # Write the number of pages crawled
    f.write("Unique pages crawled: " + str(len(urls_visited)))
    f.write(os.linesep)
    f.write(os.linesep)

    # Write the info for the longest webpage crawled
    f.write("Longest page:")
    f.write(os.linesep)
    f.write("url - " + largest_webpage[0])
    f.write(os.linesep)
    f.write("words - " + largest_webpage[1])
    f.write(os.linesep)
    f.write(os.linesep)

    # Write out the 50 most common words
    f.write("List of 50 most common words:")
    f.write(os.linesep)

    # Sort the list by the values, and output the first 50
    sorted_words = sorted(words_found.items(), key=lambda kv: kv[1])
    for i in range(50):
        f.write(sorted_words[i][0] + " --> " + sorted_words[i][1])
        f.write(os.linesep)

    f.write(os.linesep)

    # Write out the subdomains explored in ics.uci.edu
    f.write("Subdomains explored in *.ics.uci.edu:")
    f.write(os.linesep)

    # List each subdomain and the number of paths at that subdomain
    subdomains = compute_subdomain_visits("ics.uci.edu")
    for s in subdomains:
        f.write(s[0] + " --> " + s[1])
        f.write(os.linesep)

    f.write(os.linesep)

    f.close()
