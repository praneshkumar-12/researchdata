import pandas as pd

pd.set_option("display.max_colwidth", None)


def read_source_file(source_file):
    return pd.read_csv(source_file, encoding="utf-8")


def load_source_readers(source_files):
    return [pd.read_csv(source_file, encoding="utf-8") for source_file in source_files]


def extract_issn_parts(issn):
    issn_split = issn.split(" ")
    if len(issn_split) == 2:
        return issn_split[0].replace("-", "").lstrip("0"), issn_split[1].replace(
            "-", ""
        ).lstrip("0")
    else:
        return issn_split[0].replace("-", "").lstrip("0"), None


def search_sources_for_issn(source_readers, issn):
    for source_reader in source_readers:
        result = source_reader[source_reader["PrintISSN"].str.contains(issn, na=False)]
        if not result.empty:
            return result.iloc[0].to_dict()

        result = source_reader[source_reader["EISSN"].str.contains(issn, na=False)]
        if not result.empty:
            return result.iloc[0].to_dict()

    return None


def get_attribute(result, key, default=None):
    return result.get(key, default)


def print_results(
    title=None,
    issn=None,
    old_publication_name=None,
    new_publication_name=None,
    old_publisher_name=None,
    new_publisher_name=None,
    file=None,
):
    if not file:
        raise ValueError("File handler not specified!")
    if title:
        print("Title:", title, file=file)
    if issn:
        print("ISSN:", issn, file=file)
    if old_publication_name:
        print("Old Publication Name:", old_publication_name, file=file)
    if new_publication_name:
        print("New Publication Name:", new_publication_name, file=file)
    if old_publisher_name:
        print("Old Publisher Name:", old_publisher_name, file=file)
    if new_publisher_name:
        print("New Publisher Name:", new_publisher_name, file=file)


def update_df(row, new_df, new_publication_name, new_publisher_name):
    new_df.at[row.name, "publication_name"] = new_publication_name
    new_df.at[row.name, "publisher"] = new_publisher_name
    new_df.at[row.name, "indexing"] = "Scopus"


def process_row(row, source_readers, new_df, file):
    issn = str(row["ISSN"])
    title = str(row["title"])
    old_publication_name = str(row["publication_name"])
    old_publisher_name = str(row["publisher"])
    print_results(
        title=title,
        issn=issn,
        old_publication_name=old_publication_name,
        old_publisher_name=old_publisher_name,
        file=file,
    )

    issn_1, issn_2 = extract_issn_parts(issn)

    result = search_sources_for_issn(source_readers, issn_1)

    if result is not None:
        new_publication_name = get_attribute(result, "Title")
        new_publisher_name = get_attribute(result, "Publisher", old_publisher_name)
        print_results(
            new_publication_name=new_publication_name,
            new_publisher_name=new_publisher_name,
            file=file,
        )
        update_df(row, new_df, new_publication_name, new_publisher_name)
        return True

    if issn_2:
        result = search_sources_for_issn(source_readers, issn_2)
        if result is not None:
            new_publication_name = get_attribute(result, "Title")
            new_publisher_name = get_attribute(result, "Publisher")
            print_results(
                new_publication_name=new_publication_name,
                new_publisher_name=new_publisher_name,
                file=file,
            )
            update_df(row, new_df, new_publication_name, new_publisher_name)
            return True

    print("Not Found!", file=file)

    return False


def main():
    df = read_source_file("files/input/publications.csv")
    new_df = df.copy()

    source_files = [
        "files/input/accepted-titles-feb-2024.csv",
        "files/input/discontinued-feb-2024.csv",
        "files/input/scopus-book-series.csv",
        "files/input/scopus-sources-oct-2023.csv",
        "files/input/serial-conference-proceedings.csv",
    ]

    source_readers = load_source_readers(source_files)
    count = 0

    with open("files/logs/scopus_result.txt", "w+", encoding="utf-8") as f:
        for index, row in df.iterrows():
            print("==================================================", file=f)
            r = process_row(row, source_readers, new_df, f)
            if r:
                count += 1
        print(count, file=f)

    new_df.to_csv("files/temp_results/scopus_publications.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
