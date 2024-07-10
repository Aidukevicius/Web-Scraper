import json
import pandas as pd
from urllib.parse import urlparse

# Load JSON data
with open('results_all_keywords.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter businesses
filtered_results = []
for item in data:
    website = item.get('website', '').lower()

    # Function to check if website is from Facebook, Instagram, or Google Ads Services
    def is_desired_website(url):
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'www.facebook.com' or parsed_url.netloc == 'www.instagram.com':
            return True
        if 'googleleadsservices' in parsed_url.netloc or 'googleadservices' in parsed_url.netloc:
            return True
        return False

    # Check if no website or website is from Facebook, Instagram, or Google Ads Services
    if not website or is_desired_website(website):
        filtered_results.append({
            'Business Name': item.get('title', ''),
            'Phone Number': item.get('phone', '')
        })

# Save filtered results to Excel
df = pd.DataFrame(filtered_results)
filename = 'filtered_results.xlsx'
df.to_excel(filename, index=False)
print(f"Filtered data saved to {filename}")
