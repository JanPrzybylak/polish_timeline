import scrapy
import re
import unicodedata

class WarsawHistorySpider(scrapy.Spider):
    name = "warsaw_history"
    start_urls = [
        'https://en.wikipedia.org/wiki/Timeline_of_Warsaw'
    ]

    categories = {
        "war": ["battle", "war", "invade", "siege", "uprising", "army", "military", "revolt", "occupation", "artillery"],
        "science": ["university", "academy", "research", "institute", "science", "scientific", "astronomy", "education", "college"],
        "culture": ["theatre", "museum", "concert", "festival", "art", "exhibition", "cultural", "library"],
        "sports": ["championship", "team", "football", "basketball", "sport", "athlete", "olympic"],
        "religion": ["church", "cathedral", "religion", "diocese", "monastery", "bishop", "christian"],
        "politics": ["sejm", "mayor", "law", "governor", "rights", "magdeburg", "constitution", "election", "parliament", "diet", "confederation", "elections"]
    }

    def normalize_text(self, text):
        """Normalize dashes and unicode artifacts."""
        text = unicodedata.normalize("NFKD", text)
        text = text.replace("–", "-").replace("—", "-")  # En dash, Em dash to ASCII dash
        return text

    def categorize_event(self, text):
        text = text.lower()
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text):
                    return category
        return "other"

    def parse(self, response):
        for li in response.css('div.mw-parser-output > ul > li'):
            year_text = li.css('::text').get()
            full_text = li.css('::text').getall()
            if year_text and len(full_text) > 1:
                description = ' '.join([
                    self.normalize_text(t.strip()) 
                    for t in full_text if t.strip()
                ])
                year = self.normalize_text(year_text.strip().split()[0])
                yield {
                    'year': year,
                    'description': description,
                    'category': self.categorize_event(description)
                }
