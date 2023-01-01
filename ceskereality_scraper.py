from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from datetime import datetime
import time

MAIN_LINK = "https://www.ceskereality.cz/prodej/bez-drazeb/byty/byty-2-kk/kraj-hlavni-mesto-praha/?d_subtyp=205%2C206%2C207"
COOKIES_BUTTON_CLASS = "button button--filled button__acceptAll"
LISTING_CLASS_EVEN = "div_nemovitost suda"
LISTING_CLASS_ODD = "div_nemovitost licha"
LISTING_CLASS = "div_nemovitost_foto_i"
PRICE_ELEM_CLASS = "h4 fw-bold"
TIMEOUT = 60 # seconds

results = []

driver = webdriver.Firefox()
driver.get(MAIN_LINK)
time.sleep(15)

iframes = driver.find_elements(By.XPATH, "//div[@id='appconsent']//iframe")
print('Number of iframes: ', len(iframes))
driver.switch_to.frame(iframes[0])
# Click button to accpet cookies
driver.find_element(By.XPATH, '//button[contains(@class, "button--filled button__acceptAll")]').click()
# for button in buttons:
#     print(button.get_attribute('class'))
# print(len(buttons))
time.sleep(15)
driver.switch_to.parent_frame()
total_listing_count = int(
    WebDriverWait(driver, TIMEOUT).until(
        EC.visibility_of_element_located((By.XPATH, '//span[@class="number"]'))
    ).text
)
current_page = 1
processed_listings = 0
print(total_listing_count)
while (processed_listings < total_listing_count) or (len(elements) != 0):
    if current_page != 1:
        driver.get(MAIN_LINK + '&strana=' + str(current_page))
    
    # Get all property listings on a page
    try:
        elements = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, f'//div[contains(@class, "{LISTING_CLASS}")]//a'))
        )
    except TimeoutException:
        # Case when there is an empty page as the last page
        elements = []
    driver.implicitly_wait(TIMEOUT)
    for element in elements:
        href = element.get_attribute('href')
        #open new window with specific href
        driver.execute_script("window.open('" + href +"');")
        # switch to new window
        driver.switch_to.window(driver.window_handles[1])
        price = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='price'] "))
        )
        temp_dict = {'Cena': price.text}
        # Get title element which contains disposition and location as subelements
        title_element = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='title'] "))
        )
        disposition_string = title_element.find_element(By.XPATH, ".//h1").text
        location_string = title_element.find_element(By.XPATH, ".//h2").text
        temp_dict.update({'Disposition': disposition_string})
        temp_dict.update({'Location': location_string})
        table = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, "//tbody"))
        )
        names = table.find_elements(By.XPATH, ".//th")
        values = table.find_elements(By.XPATH, ".//td")
        for name, value in zip(names, values):
            temp_dict.update({name.text: value.text})
        
        results.append(temp_dict)
        driver.implicitly_wait(10)
        driver.close()
        #back to main window
        driver.switch_to.window(driver.window_handles[0])
    processed_listings += len(elements)
    print(processed_listings)
    current_page += 1

driver.quit()
print(len(results))
with open(f"ceskereality_result_list_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as result_file:
    pickle.dump(results, result_file)