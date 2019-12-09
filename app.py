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

driver = webdriver.Firefox()

driver.wait = WebDriverWait(driver, 10)
driver.get(start_url)
# Open "Search Neighborhood" Accordion
driver.find_elements_by_class_name("accordion-group")[-1].click()
# Fill out the form.
select_township = Select(driver.find_element_by_xpath('//*[@id="ctl00_phArticle_ctlPropertySearch_ctlNeighborhoodSearch_ddlTownship"]'))
select_township.select_by_visible_text(TOWNSHIP)
sleep(0.5)
select_neighborhood = Select(driver.find_element_by_xpath('//*[@id="ctl00_phArticle_ctlPropertySearch_ctlNeighborhoodSearch_ddlNeighborhood"]'))
select_neighborhood.select_by_value(NEIGHBORHOOD_CODE)
select_prop_type = Select(driver.find_element_by_xpath('//*[@id="ctl00_phArticle_ctlPropertySearch_ctlNeighborhoodSearch_ddlClasification"]'))
select_prop_type.select_by_value(PROPERTY_CLASS)
driver.find_element_by_xpath('//*[@id="ctl00_phArticle_ctlPropertySearch_ctlNeighborhoodSearch_btnSearch"]').click()
sleep(3)

output = []
nextExists=True
page_n = 0
while nextExists:
    print(f"Scraping page {page_n}")
    page_n += 1
    sleep(1)
    rows = driver.find_elements_by_xpath("//tr")
    r = rows[0]
    col_names = [c.text for c in r.find_elements(By.TAG_NAME, "th")]
    for r in rows[1:]:
        vals = r.find_elements(By.TAG_NAME, "td")
        out = {col_names[i] : vals[i].text for i in range(0,len(col_names))}
        out["value"] = int(out['Total Assessed Value'].replace(",","").replace("$",""))
        output.append(out)
    sleep(4)
    if len(driver.find_elements_by_link_text("Next")) == 0:
        nextExists = False
    driver.find_element_by_link_text("Next").click()

# Create a CSV
df = pd.DataFrame(output)
print(f"Successfully collected a list of {len(output)} properties- now fetching detailed information on each.")

new_output = []
start_adding = True # set to false for hot starts
for ind, (addr,
          build_value_str,
          bld_sq_footage,
          city,
          class_code,
          land_value,
          nbrhd,
          pin,
          total_value,
          unit,
          value) in df.sort_values(by=["Unit", 'value']).iterrows():
    if start_adding == False:
        if new_output[-1]['pin'] == pin:
            start_adding = True
        continue
    url = "https://www.cookcountyassessor.com/Property.aspx?mode=details&pin=" + pin
    driver.get(url)
    sleep(1)
    new_record = {
        'addr' : addr,
        'value' : value,
        'pin' : pin,
        'sq_ft' : int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropInfoSqFt").text.replace(',', "")),
        'land_val_2017': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValLandFirstPass").text.replace(",","")),
        'bldg_val_2017': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValBldgFirstPass").text.replace(",","")),
        'totl_val_2017':  int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValTotalFirstPass").text.replace(",","")),
        'land_val_2016': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValLandCertified").text.replace(",","")),
        'bldg_val_2016': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValBldgCertified").text.replace(",","")),
        'totl_val_2016': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblAsdValTotalCertified").text.replace(",","")),
        'mrkt_val_2017': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharMktValCurrYear").text.replace(",","").replace("$","")),
        'mrkt_val_2016': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharMktValPrevYear").text.replace(",","").replace("$","")),
        'res_type': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharResType").text,
        'res_use': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharUse").text,
        'apts': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharApts").text,
        'ext_constr': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharExtConst").text,
        'full_bath': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharFullBaths").text),
        'half_bath': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharHalfBaths").text),
        'basement': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharBasement").text,
        'attic': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharAttic").text,
        'cntl_air': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharCentAir").text,
        'fireplaces': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharFrpl").text),
        'garage': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharGarage").text,
        'age': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharAge").text),
        'bldg_sqft': int(driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharBldgSqFt").text.replace(",","")),
        'assmt_pass': driver.find_element_by_id("ctl00_phArticle_ctlPropertyDetails_lblPropCharAsmtPass").text
    }
    print(f"Collecting details on {new_record['addr']} (valued at ${new_record['value']}")
    new_output.append(new_record)

df2 = pd.DataFrame(new_output)

filename = f'{datetime.now().strftime("%Y-%m-%d")}-{TOWNSHIP}-{NEIGHBORHOOD_CODE} {PROPERTY_CLASS}.csv'
df2.to_csv(f"data/{filename}", index=False)
