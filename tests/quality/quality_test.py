import argparse
import pandas as pd
import requests
import validators
from cpdb_api import request
from multiprocessing import Process
from multiprocessing import Manager
from tqdm import tqdm


DEFAULT_TIMEOUT_PER_ROW = 8  # seconds
DEFAULT_TIMEOUT_PER_URL = 5  # seconds
FAKE_BROWSER_HEADER = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
# List of urls that are valid but can be flagged by the test as invalid for whatever reason.
# For example, some urls are valid but the server doesn't respond.
# The urls in the list will not be flagged, so the list should be kept to a reasonable size and manually checked regularly.
# This list can be moved to spreadsheet for easier management.
IGNORED_URLS = ["http://www.climatechange.gov.au"]


def detect_invalid_urls_from_dataframe(df, ignore_empty=False):
    """
    Detect invalid urls from a dataframe.
    We assumes the dataframe has a column called "reference" and it contains urls.
    Returns a dataframe contains only rows that have invalid urls.

    When ignore_empty is True,
    """
    # list of booleans indicating if the url for each row is flagged
    urls_flagged = []
    manager = Manager()
    result_dict = manager.dict()
    for index, row in tqdm(df.iterrows()):
        url = row["reference"]
        if url == "" and ignore_empty:
            urls_flagged.append(False)
            continue
        # Unflag the url if the url is in the ignored list
        if url in IGNORED_URLS:
            urls_flagged.append(False)
            continue
        # start a subprocess to check the url because it can time out
        p = Process(target=flag_url, args=(url, result_dict))
        p.start()
        p.join(timeout=DEFAULT_TIMEOUT_PER_ROW)
        p.terminate()
        if url in result_dict:
            urls_flagged.append(result_dict[url])
        else:
            # the process cannot determine if the url is valid or not
            # so we flag the url as invalid
            urls_flagged.append(True)

    return df[urls_flagged]


def flag_url(url_str, result_dict):
    """
    Check if url needs to be flagged.
    Stores the result in result_dict.
    The key of result_dict is the url and the value is True if the url needs to be flagged and False otherwise.
    Currently we only flag urls that are invalid.
    """
    # sometimes a reference cell stores multiple urls, so we split them by newline
    urls = url_str.replace(" ", "\n").split("\n")
    result = False
    for url in urls:
        # check if url is mulformed first
        if not validators.url(url):
            result_dict[url] = True
            return
        try:
            headers = {'User-Agent': FAKE_BROWSER_HEADER}
            response = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT_PER_URL)
        except:
            # if the request times out, we flag the url
            result_dict[url] = True
            return
        # if the status code of any request is not 200, the url row needs to be flagged
        result = result or response.status_code > 400
    result_dict[url_str] = result


if __name__ == "__main__":
    # Two modes to run the function:
    # 1. automatic mode:
    #    the script will run as a github action every week,
    #    examines the API result at head and upload the
    #    flagged urls to a google sheet.
    # 2. manual mode: the script can run with local csv file and output to local csv file.
    # optional argument 1: path to the csv file
    parser = argparse.ArgumentParser(
        description="Commandline tool to check the quality of reference URLs in CPDB."
    )
    parser.add_argument(
        "-i",
        "--input_csv",
        help="Path to the input csv file. If it's not provided, we default to download data from cpdb-api. The csv should contain a column named reference.",
    )
    parser.add_argument(
        "-o",
        "--output_csv",
        help="Path to the output csv file. If it's not provided, we default to upload data to a google sheet.",
    )
    # Other potential arguments:
    # 1. ignore_empty: ignore empty urls when flagging rows
    # 2. pass in the list of ignored urls as a separate list.
    # 3. change destination of where to upload the flagged urls.

    args = parser.parse_args()
    # Load inputs
    if args.input_csv:
        print("Read input from local CSV file. Path: " + args.input_csv)
        df = pd.read_csv(args.input_csv)
        if "reference" not in df.columns:
            raise ValueError(
                "The input csv file should contain a column named `reference`. Found columns: "
                + df.columns
            )
    else:
        print("Download input from cpdb-api.")
        r = request.Request()
        df = r.issue()
        print("Downloaded " + str(df.shape[0]) + " rows from cpdb-api.")

    if not args.output_csv:
        import gspread
        from datetime import datetime

    flagged_rows = detect_invalid_urls_from_dataframe(df)
    flagged_rows = flagged_rows.fillna('')

    # Output results
    if args.output_csv:
        print("Write output to local CSV file. Path: " + args.output_csv)
        flagged_rows.to_csv(args.output_csv)
    else:
        print("Upload output to google sheet.")
        # Flora's test sheet, need to be swapped out to a sheet owned by NewClimate
        # Steps:
        # 1. create gcp project, enable Drive API and Google Sheet API and service account
        # 2. give service account editor permission in the spreadsheet (https://docs.google.com/spreadsheets/d/1mMcAYIW9bNOb82GbYQIiGXvIi8c9qmtaLBhtjAvDe5A/edit#gid=0)
        DEFAULT_GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1mMcAYIW9bNOb82GbYQIiGXvIi8c9qmtaLBhtjAvDe5A"
        # Default cred file path, need to swap to stuff stored in github secrets
        CRED = {} # paste the cred dict here

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Authorize the credentials and create a client
        client = gspread.service_account_from_dict(CRED)

        # Open the Google Sheet by name
        sheet = client.open_by_url(DEFAULT_GOOGLE_SHEET_URL)

        
        worksheet_name = datetime.today().strftime('%Y-%m-%d')
        # Check if the worksheet exists
        try:
            worksheet = sheet.worksheet(worksheet_name)
            worksheet_exists = True
        except gspread.exceptions.WorksheetNotFound:
            pass

        # If the worksheet exists, override the value. Otherwise, create a new worksheet
        if worksheet_exists:
            worksheet.clear()
        else:
            worksheet = sheet.add_worksheet(title=datetime.today().strftime('%Y-%m-%d'), rows=str(df.shape[0] + 10), cols=str(df.shape[1]))

        # Convert the DataFrame to a list of lists and upload it to the worksheet
        data = [flagged_rows.columns.values.tolist()] + flagged_rows.values.tolist()
        worksheet.update(data)
