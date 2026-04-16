import os
import sys
import argparse
import time
from hl import hl_runner, get_url
from utils import get_xlsx_filepath
from worker import (
    merge_csv_to_xlsx,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, help="id worker")
    parser.add_argument("--sheet", type=str, help="sheet name")
    parser.add_argument("--url", type=str, help="sheet name")

    args = parser.parse_args()
    # out = "hl.xlsx"
    # xlsx_out = os.path.join(os.getcwd(), "spreadsheet", out)
    xlsx_out = get_xlsx_filepath("hl.xlsx")
    if args.url:
        get_url(args.url)

    if args.id and args.sheet:
        start = time.perf_counter()
        hl_runner(id_worker=int(args.id), max_workers=5, sheet=args.sheet)
        elapsed = time.perf_counter() - start
        print(f"Execution time: {elapsed:.2f} seconds.")

    elif args.sheet:
        merge_csv_to_xlsx(
            xlsx_out, ["name", "isin", "url", "keyword"], args.sheet)


if __name__ == "__main__":
    main()
