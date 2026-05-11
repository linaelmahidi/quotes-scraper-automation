import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from supabase import create_client

# 1. Verbinding maken via veilige 'Environment Variables'
# GitHub Actions vult deze straks automatisch in vanuit je 'Secrets'
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. De Scraper (voorbeeld gebaseerd op quotes)
url = "https://quotes.toscrape.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
quotes_html = soup.find_all("div", class_="quote")

scrape_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
rows = []

for quote in quotes_html:
    content = quote.find("span", class_="text").text
    speaker = quote.find("small", class_="author").text
    tags = [tag.text for tag in quote.find_all("a", class_="tag")]
    
    # Berekeningen (Enrichment)
    word_count = len(content.split())
    length_tier = "Kort" if word_count < 15 else ("Medium" if word_count < 30 else "Lang")
    tag_richness = "Enkelvoudig" if len(tags) <= 1 else ("Divers" if len(tags) <= 3 else "Zeer Divers")

    rows.append({
        "content": content,
        "speaker": speaker,
        "number_of_tags": len(tags),
        "link_to_author": f"{url}{quote.find('a')['href']}",
        "collection_date": "2026-05-12", # Pas dit aan indien nodig
        "scraped_at": scrape_time,
        "word_count": word_count,
        "length_tier": length_tier,
        "tag_richness": tag_richness
    })

# 3. Push naar Supabase
try:
    if rows:
        supabase.table("quotes").insert(rows).execute()
        print(f" Succesvol {len(rows)} rijen toegevoegd op {scrape_time}")
    else:
        print(" Geen data gevonden om te uploaden.")
except Exception as e:
    print(f" Fout bij uploaden: {e}")