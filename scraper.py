import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, SoupStrainer


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # TODO: Implement function to extract the next link.

    # List of links to return
    links = list()

    # Check the status integer
    #   status 200-399: OK, use the html retrieved in resp.raw_response.content to return list of links
    #   status 400-599: HTTP ERROR, use resp.raw_response to report the error and return empty list
    #   status 600-609: CACHING ERROR, use resp.error to report the error and return empty list

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        # TODO: get the links from the http response and add them to the list

        # PSEUDOCODE
        # Parse resp.raw_response.content for the links in the webpage
        #   USE BeautifulSoup
        for link in BeautifulSoup(resp.raw_response.content, parse_only=SoupStrainer('a')):
            if link.has_attr('href'):

                href = urlparse(link['href'])

                # If netloc is false, the href is relative: add the href to the end of the url
                if not href.netloc:
                    href = url + "/" + href

                if is_valid(href, resp):
                    links.append(href)

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
        "codeyhuntting.repl.co"
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

        # Check if the url is too similar to the response content

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
