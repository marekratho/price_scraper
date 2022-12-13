from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pickle
from datetime import datetime

MAIN_LINK = "https://www.sreality.cz/hledani/prodej/byty/praha-1,praha-2,praha-3,praha-4,praha-5,praha-6,praha-7,praha-8,praha-9,praha-10?velikost=1%2B1,2%2Bkk,2%2B1,3%2Bkk,3%2B1&stavba=panelova,cihlova&strana="
COOKIE_CONSENT_BUTTON_CLASS = "scmp-btn scmp-btn--default sm-max:scmp-ml-sm md:scmp-ml-md lg:scmp-ml-dialog"
TIMEOUT = 30
counter = 1
driver = webdriver.Firefox()
driver.get(MAIN_LINK + str(counter))
# Agree to cookies
driver.implicitly_wait(TIMEOUT)


allow_cookie_button = WebDriverWait(driver, TIMEOUT).until(
    EC.url_matches("https://www.seznam.cz/nastaveni-souhlasu/")
)

time.sleep(5)
print(driver.page_source)
#driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])

time.sleep(5)
WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div"))).click()


ActionChains(driver)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .perform()
time.sleep(5)
ActionChains(driver)\
    .send_keys(Keys.ENTER)\
    .send_keys(Keys.RETURN)\
    .perform()


results = []
# How many listings are on sreality?
displayed_results = driver.find_elements(By.XPATH, '//span[@class="numero ng-binding"]')
all_listings_count = int(displayed_results[1].text.replace(' ',''))
print(all_listings_count)
end_reached = False
processed_listings = 0
while not end_reached:
    time.sleep(15)
    current_page_listings = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="property ng-scope"]')))
    print(len(current_page_listings))
    for listing in current_page_listings:
        price_subelement = listing.find_element(By.XPATH, './/span[@class="price ng-scope"]')
        price = price_subelement.text
        try:
            price = price.replace(' Kč', '')
            price = price.replace(' ', '')
            price = int(price)
        except ValueError:
            price = -1
        print(price_subelement.text)
        name_subelement = listing.find_element(By.XPATH, './/span[@class="name ng-binding"]')
        name = name_subelement.text
        name = name.replace('Prodej bytu ', '')
        parts = name.split()
        disposition = parts.pop(0)
        area = ''.join(parts)
        location_subelement = listing.find_element(By.XPATH, './/span[@class="locality ng-binding"]')
        location = location_subelement.text
        print(disposition, ' ', area)
        print(location)
        print(price)
        results.append({
            'disposition': disposition, 'area': area, 
            'location': location, 'price': price
        })
    # Check if end of page has been reached
    processed_listings += 20
    if processed_listings > all_listings_count:
        end_reached = True
    else:
        counter += 1
        driver.get(MAIN_LINK + str(counter))

time.sleep(10)
print('Finally done')
with open(f"sreality_result_list_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as result_file:
    pickle.dump(results, result_file)

driver.quit()
