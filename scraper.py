import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, SoupStrainer

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

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # List of links to return
    links = list()

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        soup = BeautifulSoup(resp.raw_response.content)

        # Count the words in the soup, excluding stop words (we could also use our tokenizer here, but this works too)
        words = re.findall(r'\w+', soup.get_text())
        words = [w for w in words if w not in stopwords]

        # Only hunt the links down if there are more than 200 words
        if len(words) > 200:
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

        # TODO: Check if the html at the url is too similar to the response content

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
