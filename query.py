import os
import csv
import ast
import bs4
import time
from selenium import webdriver

SUMMARIZE_ONLY = True

WEBSITE_LINK = r"https://programs.dsireusa.org"
BASE_LINKS = [
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=PA",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=RI",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=SC",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=SD",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=TN",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=UT",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=VT",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=WV",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=WI",
    r"https://programs.dsireusa.org/system/program?fromSir=0&state=WY"
]

CHROME_DRIVER_PATH = r"/Users/evanputnam/Downloads/chromedriver"

def write_to_file(data_list, state):
    with open(state+"_"+"results.txt", "w+") as fle:
        fle.write(str(data_list))
        fle.write('\n')

def summarize_results_files():
    lst = []
    for root, dirs, files in os.walk(os.getcwd()):
        for fle in files:
            if "_results.txt" in fle:
                with open(os.path.join(root, fle)) as fle_read:
                    lines = fle_read.read()
                    print(lines)
                    lst.append([ast.literal_eval(lines), fle])
    with open("aggregate.csv", "w+") as fle_write:
        csv_reader = csv.writer(fle_write)
        for elems in lst:
            for elem in elems[0]:
                url = elem[0]
                state = elems[1].split("_")[0].strip()
                data = elem[1]
                csv_reader.writerow([url, state, data])


def _get_data_on_page(link):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    try:
        driver.get(link)
    except:
        driver.quit()
        return None
    time.sleep(2)

    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    cols = soup.find_all("li", {"data-ng-repeat":"field in programFields"})
    
    eligable = ""
    commercial = False
    for col in cols:
        temp = col.find("div", {"class":"ng-binding"})
        if "Eligible Efficiency Technologies" in temp.text:
            eligable = col.find("div",{"on-last-repeat":"detail-overview"}).text
        if "Applicable Sectors:" in temp.text:
            commercial = "Commercial" in col.find("div",{"on-last-repeat":"detail-overview"}).text

    eligLower = eligable.lower()
    if eligable == "" or commercial == False:
        driver.quit()
        return None
    elif "hvac" in eligLower or "air conditioners" in eligLower or "heat pumps" in eligLower:
        driver.quit()
        return [link, eligable]
    driver.quit()
    return None

def get_data_on_pages(links):
    lst = []
    for i in range(0, len(links)):
        commercial_viable = _get_data_on_page(links[i])
        if commercial_viable != None:
            lst.append(commercial_viable)
    return lst

def get_state_data(base_link):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get(base_link)
    time.sleep(3)
    select = webdriver.support.ui.Select(driver.find_element_by_name("DataTables_Table_0_length"))
    select.select_by_value("-1")
    time.sleep(3)
    
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    div_elem_odd = soup.find_all("tr", {"role":"row", "class":"odd"})
    div_elem_even = soup.find_all("tr", {"role":"row", "class":"odd"})

    lst_of_new_links = []
    for i in div_elem_odd:
        if "Financial Incentive" in i.find_all("td")[2] and "US" not in i.find_all("td")[1]:
            link = (WEBSITE_LINK + str(i.find("a")['href']))
            lst_of_new_links.append(link)
    for i in div_elem_even:
        if "Financial Incentive" in i.find_all("td")[2] and "US" not in i.find_all("td")[1]:
            link = (WEBSITE_LINK + str(i.find("a")['href']))
            lst_of_new_links.append(link)


    driver.quit()
    return lst_of_new_links

if __name__ == "__main__":
    if not SUMMARIZE_ONLY:
        for i in BASE_LINKS:
            temp = i.split("=")
            state = temp[len(temp)-1]
            print(state)
            links_to_parse = get_state_data(i)
            data_to_write = get_data_on_pages(links_to_parse)
            write_to_file(data_to_write, state)
    summarize_results_files()