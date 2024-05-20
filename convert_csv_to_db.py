import pandas as pd

# row headers
"""
Serial Number	UniqueID	Title	Academic Year	First Author	Second Author	Third Author	Other Authors	Is Student Author	Student Name	Student Batch	Specification	Publication Type	Publication Name	Publisher	Publication Year	Publication Month	Volume	Page Numbers	Indexing	Quartile	Citations	DOI	FPP	URL	ISSN
"""

# order of columns
"""
uniqueid
title
start_academic_month
start_academic_year
end_academic_month
end_academic_year
first_author
second_author
third_author
other_authors
is_student_author
student_name
student_batch
specification
publication_type
publication_name
publisher
year_of_publishing
month_of_publishing
volume
page_number
indexing
quartile
citation
doi
front_page_path
url
ISSN
verified
admin_verified
"""

headers = [
    "Serial Number",
    "UnqiueID",
    "Title",
    "Academic Year",
    "First Author",
    "Second Author",
    "Third Author",
    "Other Authors",
    "Is Student Author",
    "Student Name",
    "Student Batch",
    "Specification",
    "Publication Type",
    "Publication Name",
    "Publisher",
    "Publication Year",
    "Publication Month",
    "Volume",
    "Page Numbers",
    "Indexing",
    "Quartile",
    "Citations",
    "DOI",
    "FPP",
    "URL",
    "ISSN",
]

order_of_columns = [
    "uniqueid",
    "title",
    "start_academic_month",
    "start_academic_year",
    "end_academic_month",
    "end_academic_year",
    "first_author",
    "second_author",
    "third_author",
    "other_authors",
    "is_student_author",
    "student_name",
    "student_batch",
    "specification",
    "publication_type",
    "publication_name",
    "publisher",
    "year_of_publishing",
    "month_of_publishing",
    "volume",
    "page_number",
    "indexing",
    "quartile",
    "citation",
    "doi",
    "front_page_path",
    "url",
    "issn",
    "verified",
    "admin_verified",

]

# Read the CSV file
def read_csv(filename):
    df = pd.read_csv(filename)
    return df


def process_rows(df, filename):
    # drop serial number
    df = df.drop(columns=["Serial Number"])


    # convert academic year to start_academic_year, start_academic_month, end_academic_year, end_academic_month
    # Eg: JUL 2020 - JUN 2021 to JUL, 2020, JUN, 2021
    df["start_academic_month"] = df["Academic Year"].apply(lambda x: x.split(" ")[0])
    df["start_academic_year"] = df["Academic Year"].apply(lambda x: x.split(" ")[1])
    df["end_academic_month"] = df["Academic Year"].apply(lambda x: x.split(" ")[3])
    df["end_academic_year"] = df["Academic Year"].apply(lambda x: x.split(" ")[4])

    # drop academic year
    df = df.drop(columns=["Academic Year"])

    # rename Publication Year to year_of_publishing
    df.rename(columns={"Publication Year": "year_of_publishing"}, inplace=True)

    # rename Publication Month to month_of_publishing
    df.rename(columns={"Publication Month": "month_of_publishing"}, inplace=True)

    # rename Page Numbers to page_numbers
    df.rename(columns={"Page Numbers": "page_number"}, inplace=True)

    # rename Citations to citation
    df.rename(columns={"Citations": "citation"}, inplace=True)

    # set verified and admin_verified to 'False'
    df["verified"] = "False"
    df["admin_verified"] = "False"

    # rename FFP to front_page_path
    df.rename(columns={"FPP": "front_page_path"}, inplace=True)

    # convert each and every column header to its lowercase and space replaced by underscores
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # re-order the columns of the df
    df = df[order_of_columns]

    # save the file as csv file
    df.to_csv(filename, index=False)

    return df

if __name__ == "__main__":
    filename = 'research_papers_conference.csv'
    new_filename = 'research_papers_conference_db_converted.csv'
    df = read_csv(filename)
    process_rows(df, new_filename)