from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper, final_report
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.sites_crawled = 0
        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    final_report()
                    break

                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                scraped_urls = scraper(tbd_url, resp, self.logger)

                # Report the stats every so often
                self.sites_crawled += 1
                if self.sites_crawled >= 100:
                    self.sites_crawled = 0
                    self.logger.info("Downloaded 100 sites. Generating a report-so-far")
                    final_report()

                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
            except Exception:
                # If the crawler runs into any exception, spit out the final report before re-raising the exception
                self.logger.info("Worker caught an exception. Generating final report before exit.")
                final_report()
                raise
