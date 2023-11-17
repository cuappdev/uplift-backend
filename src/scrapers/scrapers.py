import c2c_scraper
import class_scraper
import pool_scraper

SCRAPED_PAGES = 10
print('Scraping...')
print("Capacities")
c2c_scraper.scrape_capacity()
print("Classes")
class_scraper.scrape_classes(SCRAPED_PAGES)
print("Pool hours")
pool_scraper.scrape_pool_hours()
print("Done scraping")
