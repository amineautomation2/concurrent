from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from pprint import pprint
from utils import find_element_or_none, find_elements, delay, find_selector, find_visibility, get_with_backoff
from typing import Literal
from re import findall
import openpyxl


def get_endpoint_by_type(fund_type: Literal["Investment", "ETF"], offset: int):
    if fund_type == "ETF":
        return f'https://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?offset={offset}&etf_search_input=etf&companyid=&sectorid='
    return f'https://www.hl.co.uk/shares/investment-trusts/search-for-investment-trusts?offset={offset}&it_search_input=p&companyid=&sectorid='


def get_funds_url(driver: WebDriver, fund_type: Literal["Investment", "ETF"], xlsx_path: str):
    offset = 0
    max_offset = 0
    page = 1
    pages = 1

    list_funds = []
    endpoint = get_endpoint_by_type(fund_type, offset)
    get_with_backoff(driver, endpoint)

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb[fund_type]
    print(f'[####] H&L {fund_type} [####]')
    wait = WebDriverWait(driver, 5)

    accept_cookies = find_element_or_none(
        wait, '//*[@id="onetrust-reject-all-handler"]')
    if accept_cookies:
        accept_cookies.click()

    page_list = find_elements(
        wait, '//table/tbody/tr[1]/td[1]/table/tbody/tr/td/a')
    if page_list:
        max_offset = (len(page_list) + 1) * 50 - 50
        pages = len(page_list) + 1

    while offset <= max_offset:
        # print(f'[#]  H&L [{page}/{pages}]')
        TABLE_XPATH = '//div[@class="table-overflow-wrapper"]/table/tbody'
        ROWS_XPATH = '//div[@class="table-overflow-wrapper"]/table/tbody/tr'
        wait.until(EC.presence_of_element_located((By.XPATH, TABLE_XPATH)))
        fund_rows = find_elements(wait, ROWS_XPATH)
        if fund_rows:
            for fund in fund_rows[1:len(fund_rows) - 1]:
                name_xpath = "./td[2]/a" if fund_type == "Investment" else "./td[5]"
                url_xpath = "./td[2]/a"
                name = fund.find_element(By.XPATH, name_xpath).text.strip()
                url = fund.find_element(
                    By.XPATH, url_xpath).get_attribute("href")

                list_funds.append(dict(name=name, url=url))
        page += 1
        offset += 50
        delay(1, 2)
        if offset <= max_offset:
            endpoint = get_endpoint_by_type(fund_type, offset)
            get_with_backoff(driver, endpoint)

    iter = 2
    for fund in list_funds:
        ws.cell(iter, 1, fund["name"])
        cell = ws.cell(iter, 3, fund["url"])
        cell.style = "Hyperlink"
        cell.hyperlink = fund["url"]
        iter += 1

    wb.save(xlsx_path)
    wb.close()
    print(f'[#] Parsed {len(list_funds)} funds into {xlsx_path}')


"""
ETF_URL_XPATH = //nav[@aria-label="Factsheet tabs"]/ul/li[3]/div/a
ETF_ISIN_XPATH = //div[@id='radix-:R3km:-content-Overview'][1]/section/div[1]/div[2]/ul/li[last()]/div/div[2]

IT_URL_XPATH = //nav[@aria-label="Factsheet tabs"]/ul/li[6]/div/a
IT_ISIN_XPATH = //div[@id="radix-:r3:-content-Overview"][1]/section/div[1]/div[2]/ul/li[6]/div/div[2]

KEYWORD_XPATH = //div[@id="__next"]/div/div[2]/header/div[3]/div[2]/ul/div/div/div/li
"""


def get_fund_keyword_it(driver: WebDriver, funds: list[dict]) -> list[dict]:
    url_xpath = '//nav[@aria-label="Factsheet tabs"]/ul/li[6]/div/a'
    url2_xpath = '//div[@id="factsheet-nav-container"]/ul/li[8]/a'
    isin_xpath = '//ul[@class="info-list_root__Vpw6y info-list_narrow__gzzia"]'
    keyword_xpath = '//div[@id="__next"]/div/div[2]/header/div[3]/div[2]/ul/div/div/div/li'
    wait = WebDriverWait(driver, timeout=10)
    data = []
    for fund in funds:
        url_backup = fund.get("url")
        try:
            name = fund["name"]
            isin, url, keyword_fmt = None, None, None
            get_with_backoff(driver, fund['url'])
            accept_cookies = find_element_or_none(
                WebDriverWait(driver, timeout=3), '//*[@id="onetrust-reject-all-handler"]')
            if accept_cookies:
                accept_cookies.click()

            url = f"{driver.current_url}/company-information"
            get_with_backoff(driver, url)
            isin = find_element_or_none(wait, isin_xpath)
            if isin:
                res = findall(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", isin.text)
                if len(res) > 0:
                    isin = res[0]
            keyword = find_elements(wait, keyword_xpath)
            if keyword:
                keyword_fmt = []
                for k in keyword:
                    keyword_fmt.append(k.text.strip())
                # keyword_fmt = f"This Stock can be held in a {', '.join(keyword_fmt)}"
                keyword_fmt = f"This stock can be held in a {', '.join(keyword_fmt[:len(keyword_fmt)-1])} or {keyword_fmt[-1]}"
            f = dict(name=name,
                     isin=isin,
                     url=url or url_backup,
                     keyword=keyword_fmt,
                     index=fund.get("index"),
                     sheet="Investment",
                     )

            data.append(f)
        except:
            print(f"error: {fund}")
        # pprint(f)
        delay(1, 2)
    return data


def get_fund_keyword_etf(driver: WebDriver, funds: list[dict]) -> list[dict]:
    url_xpath = '//nav[@aria-label="Factsheet tabs"]/ul/li[3]/div/a'
    url2_xpath = '//div[@id="factsheet-nav-container"]/ul/li[5]/a'
    # isin_xpath = '//div[@id="radix-:R3km:-content-Overview" and @data-state="active"]/section/div[1]/div[2]/ul/li[last()]/div/div[2]'
    # isin_xpath = '//ul/li/div/div[matches(., "[A-Z]{2}[A-Z0-9]{9}[0-9]")]'
    isin_xpath = '//ul[@class="info-list_root__Vpw6y info-list_narrow__gzzia"]'
    keyword_xpath = '//*[@id="__next"]/div/div[2]/header/div[3]/div[2]/ul/div/div/div/li'
    keyword_xpath = '//*[@id="__next"]/div/div/header/div[3]/div[2]/ul/div/div/div'
    keyword_xpath = '//div[@class="applicable-products_applicable_products__JsXiH"]'
    # keyword_xpath = '//div[@class="small-hide medium-hide wide-medium-hide"]'
    wait = WebDriverWait(driver, timeout=10)
    data = []
    for fund in funds:
        url_backup = fund.get("url")
        try:
            name = fund["name"]
            isin, url, keyword_fmt = None, None, None
            get_with_backoff(driver, fund['url'])

            accept_cookies = find_element_or_none(
                WebDriverWait(driver, timeout=3), '//*[@id="onetrust-reject-all-handler"]')
            if accept_cookies:
                accept_cookies.click()
            url = f"{driver.current_url}/company-information"
            get_with_backoff(driver, url)
            isin = find_element_or_none(wait, isin_xpath)
            if isin:
                res = findall(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", isin.text)
                if len(res) > 0:
                    isin = res[0]
            keyword = find_element_or_none(wait, keyword_xpath)
            if keyword:
                # keyword = keyword.text.replace("\n", ", ")
                keyword = keyword.text.split("\n")
                keyword_fmt = f"This stock can be held in a {", ".join(keyword[:len(keyword)-1])} or {keyword[-1]}"
            f = dict(name=name,
                     isin=isin,
                     url=url or url_backup,
                     keyword=keyword_fmt,
                     index=fund.get("index"),
                     sheet="ETF",
                     )

            data.append(f)
        except:
            print(f"error: {fund}",)
        # pprint(f)
        delay(1, 2)
    return data
