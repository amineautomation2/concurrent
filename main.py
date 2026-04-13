import os
import sys
import argparse
import time
from hl import hl_runner
from worker import (
    merge_csv_to_xlsx,
)


def list_of_strings(arg):
    return arg.split(',')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, help="id worker")
    parser.add_argument("--sheet", type=str, help="sheet name")
    parser.add_argument("--sheets", type=list_of_strings, help="sheet name")

    args = parser.parse_args()
    out = "hl.xlsx"
    xlsx = os.path.join(os.getcwd(), "spreadsheet", out)
    if args.id:
        # id_worker = int(sys.argv[1])
        start = time.perf_counter()
        hl_runner(int(args.id), 5)
        elapsed = time.perf_counter() - start
        print(f"Execution time: {elapsed:.2f} seconds.")
    elif args.sheet:
        merge_csv_to_xlsx(
            xlsx, ["name", "isin", "url", "keyword"], args.sheet)

    elif args.sheets:
        for s in args.sheets:
            merge_csv_to_xlsx(
                xlsx, ["name", "isin", "url", "keyword"], s)
    else:
        print("error: ", sys.argv)
        exit(1)


if __name__ == "__main__":
    main()
