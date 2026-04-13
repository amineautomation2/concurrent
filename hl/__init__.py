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


def hl_runner(id_worker: int, max_workers: int, sheet: str):
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
    match sheet:
        case "Investment":
            print(sheet)
            get_funds_url(driver, sheet, xlsx)
            funds_it = get_xlsx_data(xlsx, sheet)
            it_config = {
                "id_worker": id_worker,
                "max_workers": max_workers,
                "driver": driver,
                "funds": funds_it[:5],
                "sheet": sheet,
            }
            process_worker_batch(it_config)
            return
        case "ETF":
            get_funds_url(driver, sheet, xlsx)
            funds_etf = get_xlsx_data(xlsx, sheet)
            etf_config = {
                "id_worker": id_worker,
                "max_workers": max_workers,
                "driver": driver,
                "funds": funds_etf[:5],
                "sheet": sheet,
            }
            process_worker_batch(etf_config)
            return
        case "MF":
            funds_mf = get_xlsx_data(xlsx, sheet)
            mf_config = {
                "id_worker": id_worker,
                "max_workers": max_workers,
                "driver": driver,
                "funds": funds_mf[:5],
                "sheet": sheet,
            }

            process_worker_batch(mf_config)
            get_funds_url_mf(xlsx)
            return

    driver.quit()


def process_worker_batch(config: dict):
    driver = config["driver"]
    funds = config["funds"]
    sheet = config["sheet"]
    id_worker = config["id_worker"]
    max_workers = config["max_workers"]
    funds_per_worker = get_data_by_worker_id(id_worker, max_workers, funds)
    out_csv = f"hl_{id_worker}_{sheet.lower()}.csv"
    fields = ["index", "name", "isin", "url", "keyword", "sheet"]
    if sheet == "Investment":
        funds_with_keywords = get_fund_keyword_it(driver, funds_per_worker)
        write_csv_by_id(out_csv, funds_with_keywords, fields)

    elif sheet == "ETF":
        funds_with_keywords = get_fund_keyword_etf(driver, funds_per_worker)
        write_csv_by_id(out_csv, funds_with_keywords, fields)
    elif sheet == "MF":
        funds_with_keywords = get_fund_keyword_mf(driver, funds_per_worker)
        write_csv_by_id(out_csv, funds_with_keywords, fields)
    # print(funds_with_keywords)
