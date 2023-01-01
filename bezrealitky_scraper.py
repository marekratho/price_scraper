

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from datetime import datetime
import time

MAIN_LINK = "https://www.bezrealitky.cz/vyhledat?offerType=PRODEJ&estateType=BYT&disposition=DISP_1_1%2FDISP_2_KK%2FDISP_2_1%2FDISP_3_KK%2FDISP_3_1&order=TIMEORDER_DESC&regionOsmIds=R435541&osm_value=Praha%2C+%C4%8Cesko&page="
LISTING_CLASS = "PropertyCard_propertyCardImageHolder__Kn1CN mb-3 mb-md-0 me-md-5 propertyCardImageHolder"
PRICE_ELEM_CLASS = "h4 fw-bold"
TIMEOUT = 20 # seconds

results = []

driver = webdriver.Firefox()
driver.get(MAIN_LINK+str(1))
# Agree to cookies
driver.implicitly_wait(TIMEOUT)
allow_cookie_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
allow_cookie_button.click()

listings_pages = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, f'//a[@class="page-link"]')))
last_page = int(listings_pages[-2].text)

for i in range(1, last_page + 1):
    if i != 1:
        driver.get(MAIN_LINK + str(i))
    
    # Get all property listings on a page
    try:
        elements = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="{LISTING_CLASS}"]//a'))
        )
    except TimeoutException:
        # Case when there is an empty page as the last page
        elements = []
    driver.implicitly_wait(TIMEOUT)
    for element in elements:
        # Slow down of opening of the pages
        time.sleep(2)
        #get href
        href = element.get_attribute('href')
        print(href)
        #open new window with specific href
        driver.execute_script("window.open('" + href +"');")
        # switch to new window
        driver.switch_to.window(driver.window_handles[1])
        tables = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//tbody"))
        )
        
        price = driver.find_element(By.XPATH, "//strong[@class='h4 fw-bold']")
        temp_dict = {'Cena': price.text}
        for table in tables:
            names = table.find_elements(By.XPATH, ".//th")
            values = table.find_elements(By.XPATH, ".//td")
            for name, value in zip(names, values):
                temp_dict.update({name.text: value.text})
        results.append(temp_dict)
        
        #close the new window
        driver.implicitly_wait(10)
        driver.close()
        #back to main window
        driver.switch_to.window(driver.window_handles[0])

driver.quit()
print(len(results))
with open(f"bezrealitky_result_list_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as result_file:
    pickle.dump(results, result_file)

