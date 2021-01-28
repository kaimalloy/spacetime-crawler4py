import re
from urllib.parse import urlparse

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
    #   status 600-609: CACHING ERROR, use resp.error to report the error

    # Response status OK, retrieve the links and add them
    if 200 <= resp.status < 400:
        # TODO: get the links from the http response and add them to the list

        # PSEUDOCODE
        # Parse resp.raw_response.content for the links in the webpage
        #   (will this use the text processor from Assignment 1?)
        # Remove invalid links from the list
        # Return the list

        links = list()

    # A standard http error has occurred
    elif 400 <= resp.status < 600:
        # TODO: report the http error
        pass

    # A server caching error has occurred
    else:
        # TODO: report the server caching error
        pass

    return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        # Only allow http schemes
        if parsed.scheme not in {"http", "https"}:
            return False
        # Only allow url's that have this hostname
        if "ics.uci.edu" not in parsed.hostname:
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
        print("TypeError for ", parsed)
        raise

