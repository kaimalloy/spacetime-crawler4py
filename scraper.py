import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tokenizer import PartA as tk

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

web_fingerprints = []

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # List of links to return
    links = list()

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        # Build the soup of the HTML content
        soup = BeautifulSoup(resp.raw_response.content)

        # Count the words in the soup, excluding stop words (we could also use our tokenizer here, but this works too)
        words = tk.tokenize(soup.get_text())
        words = [w for w in words if w not in stopwords]

        if len(words) > 200:
            # Create the fingerprint of the website
            fingerprint = simhash(words)
            print("Generated fingerprint for url", url, ":", fingerprint)

            for fprint in web_fingerprints:
                # If this website is too similar to another website in the list,
                # return an empty list of links
                if bitwise_similarity(fingerprint, fprint) > 0.95:
                    web_fingerprints.append(fingerprint)
                    return links

            # Append the fingerprint to the list
            web_fingerprints.append(fingerprint)

            # Append all links to the list of links to return
            for link in soup.find_all('a'):
                if link.has_attr('href'):
                    links.append(link.get('href'))

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
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for", url)
        raise

def simhash(tokens):
    weight_dict = tk.computeWordFrequencies(tokens)

    bin_dict = {}
    vector = []
    fingerprint = ""

    for key in weight_dict:
        # Add the binary version of the key to the dictionary
        bin_dict[key] = bin(hash(key))

        # Check if the word is too short
        if len(bin_dict[key]) < 32:
            # TODO: this could be a problem - if too many binary strings have a bunch of zeroes appended to the end
            # then they might match as similar to another one that is not really that "similar"
            bin_dict[key] += "0" * (32 - len(bin_dict[key]))

        # Take only 32 bits
        bin_dict[key] = bin_dict[key][0:31]

        # Replace negative and b with 0
        bin_dict[key] = bin_dict[key].replace('-', '0')
        bin_dict[key] = bin_dict[key].replace('b', '0')

    # Iterate over all the keys in the dictionary
    for key in weight_dict:
        # Iterate over all the bits in the binary strings
        for i in range(32):
            # Add the word's weight if the current bit is true, and subtract if it is false
            if bin_dict[key][i]:
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
        summation += bstr1[i] != bstr2[i]

    return summation / len(bstr1)
