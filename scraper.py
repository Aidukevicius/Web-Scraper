from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def scrape_google_maps(keyword, driver):
    try:
        driver.get(f'https://www.google.com/maps/search/{keyword}/')

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form:nth-child(2)"))).click()
        except Exception:
            pass

        # Scroll down to load more results (if needed)
        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        driver.execute_script("""
            var scrollableDiv = arguments[0];
            function scrollWithinElement(scrollableDiv) {
                return new Promise((resolve, reject) => {
                    var totalHeight = 0;
                    var distance = 1000;
                    var scrollDelay = 3000;

                    var timer = setInterval(() => {
                        var scrollHeightBefore = scrollableDiv.scrollHeight;
                        scrollableDiv.scrollBy(0, distance);
                        totalHeight += distance;

                        if (totalHeight >= scrollHeightBefore) {
                            totalHeight = 0;
                            setTimeout(() => {
                                var scrollHeightAfter = scrollableDiv.scrollHeight;
                                if (scrollHeightAfter > scrollHeightBefore) {
                                    return;
                                } else {
                                    clearInterval(timer);
                                    resolve();
                                }
                            }, scrollDelay);
                        }
                    }, 200);
                });
            }
            return scrollWithinElement(scrollableDiv);
        """, scrollable_div)

        # Extract items from search results
        items = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')

        results = []
        for item in items:
            data = {}

            try:
                data['title'] = item.find_element(By.CSS_SELECTOR, ".fontHeadlineSmall").text
            except Exception:
                pass

            try:
                data['link'] = item.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
            except Exception:
                pass

            try:
                data['website'] = item.find_element(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction] div > a').get_attribute('href')
            except Exception:
                pass
            
            try:
                rating_text = item.find_element(By.CSS_SELECTOR, '.fontBodyMedium > span[role="img"]').get_attribute('aria-label')
                rating_numbers = [float(piece.replace(",", ".")) for piece in rating_text.split(" ") if piece.replace(",", ".").replace(".", "", 1).isdigit()]

                if rating_numbers:
                   data['stars'] = rating_numbers[0]
                   data['reviews'] = int(rating_numbers[1]) if len(rating_numbers) > 1 else 0
            except Exception:
                pass

            try:
                text_content = item.text
                phone_pattern = r'((\+?\d{1,2}[ -]?)?(\(?\d{3}\)?[ -]?\d{3,4}[ -]?\d{4}|\(?\d{2,3}\)?[ -]?\d{2,3}[ -]?\d{2,3}[ -]?\d{2,3}))'
                matches = re.findall(phone_pattern, text_content)

                phone_numbers = [match[0] for match in matches]
                unique_phone_numbers = list(set(phone_numbers))

                data['phone'] = unique_phone_numbers[0] if unique_phone_numbers else None   
            except Exception:
                pass

            if data.get('title'):
                results.append(data)
        
        return results

    except Exception as e:
        print(f"Error scraping '{keyword}': {str(e)}")
        return []

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')  # Uncomment to run in headless mode (without browser UI)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    keywords = [
    "Restaurants in Detroit",
]

    all_results = []
    for keyword in keywords:
        results = scrape_google_maps(keyword, driver)
        all_results.extend(results)
        time.sleep(5)  # Adjust delay between searches as needed

    # Save all results to JSON file
    with open('results_all_keywords.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

finally:
    time.sleep(10)  # Adjust as needed to ensure data is saved before quitting
    driver.quit()
