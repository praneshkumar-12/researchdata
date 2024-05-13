import pandas as pd

pd.set_option("display.max_colwidth", None)


def load_source_file(source_file):
    return pd.read_csv(source_file, encoding="utf-8")


def load_dataset(dataset_file):
    return pd.read_csv(dataset_file, encoding="utf-8")


def filter_df(df, search_string):
    search_string = search_string.replace(".", "")
    search_terms = [term.upper() for term in search_string.split() if term.strip()]
    filtered_rows = []

    for index, row in df.iterrows():
        rowstring = " ".join(map(str, row)).upper()
        found = all(term in rowstring for term in search_terms)
        if found:
            filtered_rows.append((index, row))

    return filtered_rows


def get_academic_year(month, year):
    year = int(year)
    academic_years = [
        "JUL 2015 - JUN 2016",
        "JUL 2016 - JUN 2017",
        "JUL 2017 - JUN 2018",
        "JUL 2018 - JUN 2019",
        "JUL 2019 - JUN 2020",
        "JUL 2020 - JUN 2021",
        "JUL 2021 - JUN 2022",
        "JUL 2022 - JUN 2023",
        "JUL 2023 - JUN 2024",
    ]

    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    # Convert input to standard format
    month = month[:3].capitalize()

    # Find the academic year
    if month in ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
        academic_year = f"JUL {year} - JUN {year+1}"
    else:
        academic_year = f"JUL {year-1} - JUN {year}"

    return academic_year


def print_details(
    old_title=None,
    new_title=None,
    old_journal_name=None,
    new_journal_name=None,
    old_month=None,
    new_month=None,
    old_year=None,
    new_year=None,
    old_AY=None,
    new_AY=None,
    old_publ_type=None,
    new_publ_type=None,
    file=None,
):
    if not file:
        raise ValueError("File handler not specified!")

    if old_title is not None:
        print("Old Title:", old_title, file=file)
    if new_title is not None:
        print("New Title:", new_title, file=file)
    if old_journal_name is not None:
        print("Old Journal Name:", old_journal_name, file=file)
    if new_journal_name is not None:
        print("New Journal Name:", new_journal_name, file=file)
    if old_month is not None:
        print("Old Month:", old_month, file=file)
    if new_month is not None:
        print("New Month:", new_month, file=file)
    if old_year is not None:
        print("Old Year:", old_year, file=file)
    if new_year is not None:
        print("New Year:", new_year, file=file)
    if old_AY is not None:
        print("Old Ay:", old_AY, file=file)
    if new_AY is not None:
        print("New Ay:", new_AY, file=file)
    if old_publ_type is not None:
        print("Old Publication Type:", old_publ_type, file=file)
    if new_publ_type is not None:
        print("New Publication Type:", new_publ_type, file=file)

def month_to_number(month_name):
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    # Convert the month name to uppercase and get the corresponding number
    month_number = months.get(month_name[:3].capitalize())

    return month_number

def update_df(row, new_df, new_AY, year, month):

    start, end = new_AY.split(" - ")
    starting_month, starting_year = start.split(" ") 
    ending_month, ending_year = end.split(" ")

    new_df.at[row.name, "start_academic_month"] = starting_month
    new_df.at[row.name, "start_academic_year"] = starting_year
    new_df.at[row.name, "end_academic_month"] = ending_month
    new_df.at[row.name, "end_academic_year"] = ending_year

    new_df.at[row.name, "specification"] = "inbook"
    new_df.at[row.name, "publication_type"] = "Book Chapter"  

    new_df.at[row.name, "year_of_publishing"] = year
    new_df.at[row.name, "month_of_publishing"] = month_to_number(month) 
    
    
def process_row(row, df, new_df, f):
    title = str(row["Title"])

    filtered_rows = filter_df(df, title)

    print_details(new_title=title, file=f)

    if filtered_rows:
        filtered_row = filtered_rows[0][1].to_dict()
        filtered_index = filtered_rows[0][0]
    else:
        print("Not found", file=f)
        return False

    if filtered_row and filtered_index:
        old_title = str(filtered_row["title"])

        old_journal_name = str(filtered_row["publication_name"])
        journal_name = str(row["Journal Name"])

        old_publ_type = str(filtered_row["specification"])
        publ_type = "Book Chapter"

        old_month = str(filtered_row["month_of_publishing"])
        month = str(row["Month"])

        old_year = str(filtered_row["year_of_publishing"])
        year = str(row["Year"])

        old_AY = f'{filtered_row["start_academic_month"]} {filtered_row["start_academic_year"]} - {filtered_row["end_academic_month"]} {filtered_row["end_academic_year"]}'
        new_AY = get_academic_year(month, year)

        print_details(
            old_title=old_title,
            old_journal_name=old_journal_name,
            new_journal_name=journal_name,
            old_month=old_month,
            new_month=month,
            old_year=old_year,
            new_year=year,
            old_AY=old_AY,
            new_AY=new_AY,
            old_publ_type=old_publ_type,
            new_publ_type=publ_type,
            file=f,
        )

        update_df(row=filtered_rows[0][1], new_df=new_df, new_AY=new_AY, month=month, year=year)
    return True


def main():
    df = load_source_file("files/temp_results/journal_publications.csv")
    df = df.fillna("")

    new_df = df.copy()

    book_series_dataset = load_dataset("files/input/book_series.csv")

    count = 0


    with open("files/logs/book_series_result.txt", "w+", encoding="utf-8") as f:
        for index, row in book_series_dataset.iterrows():
            print("==================================================", file=f)
            r = process_row(row, df, new_df, f)
            if r:
                count += 1
        
        print(count, file=f)
    
    new_df = new_df.astype({"month_of_publishing": int}, errors='ignore')

    for index, row in new_df.iterrows():
        if isinstance(row["month_of_publishing"], float) or isinstance(row["month_of_publishing"], int):
            new_df.at[row.name, "month_of_publishing"] = int(row["month_of_publishing"])
        else:
             new_df.at[row.name, "month_of_publishing"] = ""
            
    
    new_df.to_csv("files/temp_results/book_series_publications.csv", index=False, encoding="utf-8")
    new_df.to_csv("files/final/final_publications.csv", index=False, encoding="utf-8")


if __name__ == "__main__": 
    main()
