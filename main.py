import os
import sys
import time
from hl import hl_runner
from worker import (
    merge_csv_to_xlsx,
)


def main():
    if len(sys.argv) == 2:
        id_worker = int(sys.argv[1])
        start = time.perf_counter()
        hl_runner(id_worker, 5)
        elapsed = time.perf_counter() - start
        print(f"Execution time: {elapsed:.2f} seconds.")
    elif len(sys.argv) == 1:
        out = "hl.xlsx"
        xlsx = os.path.join(os.getcwd(), "spreadsheet", out)
        merge_csv_to_xlsx(xlsx, ["name", "isin", "url", "keyword"], "MF")
    else:
        print("error: ", sys.argv)
        exit(1)


if __name__ == "__main__":
    main()
