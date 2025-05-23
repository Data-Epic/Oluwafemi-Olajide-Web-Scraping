import cloudscraper

url = "https://fbref.com/en/comps/9/Premier-League-Stats"
scraper = cloudscraper.create_scraper()
response = scraper.get(url)

# Save to file so you can inspect in a browser
with open("premier_league_stats.html", "w", encoding='utf-8') as file:
    file.write(response.text)

print("HTML downloaded and saved as premier_league_stats.html")

