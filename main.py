import argparse
import time

from hl import get_url, hl_runner
from utils import create_spreadsheet, get_xlsx_filepath
from worker import (
    merge_csv_to_xlsx,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, help="id worker")
    parser.add_argument("--max", type=str, help="max worker")
    parser.add_argument("--sheet", type=str, help="sheet name")
    parser.add_argument("--url", type=str, help="sheet name")
    parser.add_argument("--fresh", action="store_true", help="create fresh spreadsheet")

    args = parser.parse_args()
    # out = "hl.xlsx"
    # xlsx_out = os.path.join(os.getcwd(), "spreadsheet", out)
    xlsx_out = get_xlsx_filepath("hl.xlsx")
    if args.fresh:
        create_spreadsheet(
            xlsx_out, ["Investment", "ETF", "MF"], ["Name", "ISIN", "URL", "Keyword"]
        )

    if args.url:
        get_url(args.url)

    if args.id and args.max and args.sheet:
        hl_runner(id_worker=int(args.id), max_workers=int(args.max), sheet=args.sheet)

    elif args.sheet:
        merge_csv_to_xlsx(xlsx_out, ["name", "isin", "url", "keyword"], args.sheet)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    # driver = setup_driver(True)
    # data = get_fund_keyword(
    #    driver,
    #    [dict(url="https://www.hl.co.uk/shares/shares-search-results/BDVK708")],
    #    "Investment",
    # )
    # print(data)
    # driver.quit()
    elapsed = time.perf_counter() - start
    print(f"Execution time: {elapsed:.2f} seconds.")
