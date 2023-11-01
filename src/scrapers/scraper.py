from . import c2c_scraper, class_scraper, pool_scraper

print('Scraping...')
print("Capacities")
c2c_scraper.run_capacity_scraper()
print("Classes")
class_scraper.scrape_classes()
print("Pool hours")
pool_scraper.scrape_pool_hours()
print("Done scraping")
