import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, SoupStrainer


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, resp)]


def extract_next_links(url, resp):
    # List of links to return
    links = list()

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        soup = BeautifulSoup(resp.raw_response.content, parser='html.parser')

        # TODO: check if this page has good information content

        for link in soup.find_all('a'):
            if link.has_attr('href'):
                links.append(link.get('href'))

    # A standard http error has occurred
    elif 400 <= resp.status < 600:
        # TODO: report the http error
        pass

    # A server caching error has occurred
    else:
        # TODO: report the server caching error
        pass

    return links


def is_valid(url, resp):
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
        if not len([host for host in valid_hostnames if host in parsed.hostname]) and \
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
