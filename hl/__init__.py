from math import ceil
import os
from pprint import pprint
import openpyxl
from selenium import webdriver
from .mutual_fund import get_fund_keyword_mf, get_funds_url_mf
from .IT_ETF import get_fund_keyword_etf, get_fund_keyword_it, get_funds_url
from selenium.webdriver.chrome.webdriver import WebDriver
from utils import delay, setup_driver, get_xlsx_filepath, save_xlsx, get_with_backoff

from worker import (
    get_xlsx_data,
    get_data_by_worker_id,
    process_data,
    write_csv_by_id,
)


def hl_runner(id_worker: int, max_workers: int):
    pref = {
        # "profile.managed_default_content_settings.javascript": 2,
        # "profile.managed_default_content_settings.images": 2,
        # "profile.default_content_setting_values.notifications": 2,
        # "profile.managed_default_content_settings.stylesheets": 2,
    }
    driver = setup_driver(True, pref)
    #    driver.execute_cdp_cmd("Network.setBlockedURLs", {
    #        "urls": [
    #            # "*.google-analytics.com", "*.doubleclick.net", "*.facebook.com",
    #            "*.css", "*.png", "*.jpg", "*.gif", "*.svg", "*.woff*", "*.mp4"
    #        ]
    #    })
    #    driver.execute_cdp_cmd("Network.enable", {})
    #
    xlsx = get_xlsx_filepath("base.xlsx")
    # TODO add index to funds
    # get_funds_url(driver, "Investment", xlsx)
    # get_funds_url(driver, "ETF", xlsx)
    # get_funds_url_mf(xlsx)

    funds_etf = get_xlsx_data(xlsx, "ETF")
    funds_it = get_xlsx_data(xlsx, "Investment")
    funds_mf = get_xlsx_data(xlsx, "MF")

    hl_funds = []
    # hl_funds.extend(funds_etf)
    # hl_funds.extend(funds_it)
    # hl_funds.extend(funds_mf)

    # print(f"len it {len(funds_it)}")
    # print(f"len etf {len(funds_etf)}")
    # print(f"len mf {len(funds_mf)}")
    # print(f"len funds {len(hl_funds)}")

    # Mf
    # funds_per_worker = get_data_by_worker_id(id_worker, max_workers, funds_mf)
    # out_csv = f"hl_mf_{id_worker}.csv"
    # funds_mf = process_worker_batch(driver, out_csv, funds_per_worker)
    # print(len(funds_per_worker))

    it_config = {
        "id_worker": id_worker,
        "max_workers": max_workers,
        "driver": driver,
        "funds": funds_it[:5],
        "sheet": "Investment",
    }

    etf_config = {
        "id_worker": id_worker,
        "max_workers": max_workers,
        "driver": driver,
        "funds": funds_etf[:5],
        "sheet": "ETF",
    }

    mf_config = {
        "id_worker": id_worker,
        "max_workers": max_workers,
        "driver": driver,
        "funds": funds_mf[:5],
        "sheet": "MF",
    }

    process_worker_batch(it_config)
    process_worker_batch(etf_config)
    process_worker_batch(mf_config)
    driver.quit()


def process_worker_batch(config: dict):
    driver = config["driver"]
    funds = config["funds"]
    sheet = config["sheet"]
    id_worker = config["id_worker"]
    max_workers = config["max_workers"]
    funds_per_worker = get_data_by_worker_id(id_worker, max_workers, funds)
    out_csv = f"hl_{id_worker}_{sheet.lower()}.csv"
    if sheet == "Investment":
        funds_with_keywords = get_fund_keyword_it(driver, funds_per_worker)
    elif sheet == "ETF":
        funds_with_keywords = get_fund_keyword_etf(driver, funds_per_worker)
    else:
        funds_with_keywords = get_fund_keyword_mf(driver, funds_per_worker)
    fields = ["index", "name", "isin", "url", "keyword", "sheet"]
    write_csv_by_id(out_csv, funds_with_keywords, fields)
    print(funds_with_keywords)
    # save_xlsx(xlsx_path=xlsx, funds=funds_with_keywords, cols=cols, sheet="MF")
