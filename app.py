import argparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from time import sleep

parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser()
parser.add_argument("--nc", help='The two digit code of the neighborhood you wish to scrape e.g. "30"',
                    type=str)
parser.add_argument("--pc", help='The code of property class you wish to scrape e.g. "211"',
                    type=str)
parser.add_argument("--township", help='The township you wish to scrape - e.g. "West Chicago"', type=str)

args = parser.parse_args()

start_url = "http://www.cookcountyassessor.com/Search/Property-Search.aspx"

TOWNSHIP = args.township
NEIGHBORHOOD_CODE = args.nc
PROPERTY_CLASS = args.pc

TOWNSHIP="West Chicago"
NEIGHBORHOOD_CODE= "20"
PROPERTY_CLASS= "211"


driver = webdriver.Firefox(executable_path="./geckodriver")

driver.wait = WebDriverWait(driver, 10)
driver.get(start_url)
# Open "Search Neighborhood" Accordion
# driver.find_elements_by_class_name("accordion-group")[-1].click()
# Fill out the form.
# select_township = Select(driver.find_element_by_xpath('//*[@id="ctl00_phArticle_ctlPropertySearch_ctlNeighborhoodSearch_ddlTownship"]'))
select_township = Select(driver.find_element_by_id('edit-township'))
select_township.select_by_visible_text(TOWNSHIP)
sleep(0.5)
select_neighborhood = Select(driver.find_element_by_id('edit-neighborhood--BdfHtSp1KO4'))
select_neighborhood.select_by_value(NEIGHBORHOOD_CODE)
select_prop_type = Select(driver.find_element_by_id('edit-property-class'))
select_prop_type.select_by_value(PROPERTY_CLASS)
## get the captcha
#

cookies = driver.get_cookies()


output = []
nextExists=True
page_n = 0
while nextExists:
    print(f"Scraping page {page_n}")
    page_n += 1
    sleep(1.5)
    rows = driver.find_elements_by_xpath("//tr")
    r = rows[0]
    col_names = [c.text for c in r.find_elements(By.TAG_NAME, "th")]
    for r in rows[1:]:
        vals = r.find_elements(By.TAG_NAME, "td")
        if len(vals) == 0:
            break
        out = {col_names[i] : vals[i].text for i in range(0,len(col_names))}
        out["value"] = int(out['TOTAL\nASSESSED\nVALUE'].replace(",","").replace("$",""))
        output.append(out)
    sleep(4)
    pages = driver.find_elements_by_link_text(str(page_n+1))
    if len(pages) > 0:
        pages[0].click()
    else:
        nextExists = False
    # if len(driver.find_elements_by_link_text("Next")) == 0:
    #     nextExists = False
    # driver.find_element_by_link_text("Next").click()

# Create a CSV
df = pd.DataFrame(output)
df.to_csv('1312comps.csv')
print(f"Successfully collected a list of {len(output)} properties- now fetching detailed information on each.")


new_output = []

start_adding =True # True # set to false for hot starts
for ind, (pin, addr, unit, city,
          class_code, land_sq_footage, bld_sq_footage, land_val, bld_val, total_val, value) in df.sort_values(by=["UNIT", 'value']).iterrows():
    if start_adding == False:
        if new_output[-1]['pin'] == pin:
            start_adding = True
            print('ok all caught up now')
        continue

    url = "https://www.cookcountyassessor.com/pin/" + pin.replace('-', '')
    driver.get(url)
    sleep(1)
    driver.find_elements_by_link_text("Characteristics")[0].click()

    es = driver.find_elements_by_class_name('detail-row--detail')
    new_record = {
        'addr' : addr,
        'value' : value,
        'pin' : pin,
        'bld_sq_ft': bld_sq_footage,
        'lnd_sq_ft': land_sq_footage,
        'bld_val': bld_val,
        'land_val': land_val,

    }
    other_cols = [
        'apts', #12
        'ext_constr',
        'full_bath',
        'half_bath',
        'basement',
        'attic',
        'cntl_air',
        'fireplaces',
        'garage',
        'age',
        'bldg_sqft',
        'assmt_pass' #23
        ]

    new_record.update({other_cols[i -12 ] : es[i].text for i in range(12, min(len(es), 24))})
    print(f"Collecting details on {new_record['addr']} (valued at ${new_record['value']})")
    new_output.append(new_record)

df2 = pd.DataFrame(new_output)

filename = f'{datetime.now().strftime("%Y-%m-%d")}-{TOWNSHIP}-{NEIGHBORHOOD_CODE} {PROPERTY_CLASS}.csv'
df2.to_csv(f"{filename}", index=False)
