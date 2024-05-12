import pandas as pd

pd.set_option("display.max_colwidth", None)


def read_source_file(source_file):
    return pd.read_csv(source_file, encoding="utf-8")


def load_dataset(source_file):
    return pd.read_csv(source_file, encoding="utf-8")


def print_results(
    title=None,
    issn=None,
    old_publication_name=None,
    new_publication_name=None,
    old_publisher_name=None,
    new_publisher_name=None,
    old_indexing=None,
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
    if old_indexing:
        print("Old Indexing:", old_indexing, file=file)


def extract_issn_parts(issn):
    issn_split = issn.split(" ")
    if len(issn_split) == 2:
        return issn_split[0], issn_split[1]
    else:
        return issn_split[0], None


def search_source_for_issn(dataset, issn):
    result = dataset[dataset["PrintISSN"].str.contains(issn, na=False)]
    if not result.empty:
        return result.iloc[0].to_dict()

    result = dataset[dataset["EISSN"].str.contains(issn, na=False)]
    if not result.empty:
        return result.iloc[0].to_dict()

    return None


def get_attribute(result, key, default=None):
    return result.get(key, default)


def update_df(row, new_df, new_publication_name, new_publisher_name, old_indexing):
    new_df.at[row.name, "publication_name"] = new_publication_name
    new_df.at[row.name, "publisher"] = new_publisher_name

    if old_indexing and old_indexing != float("nan"):
        new_df.at[row.name, "indexing"] = f"{old_indexing}, Web of Sciences"
    else:
        new_df.at[row.name, "indexing"] = "Web of Sciences"


def process_row(row, dataset, new_df, file):
    issn = str(row["ISSN"])
    title = str(row["title"])
    old_publication_name = str(row["publication_name"])
    old_publisher_name = str(row["publisher"])
    old_indexing = str(row["indexing"])

    print_results(
        title=title,
        issn=issn,
        old_publication_name=old_publication_name,
        old_publisher_name=old_publisher_name,
        old_indexing=old_indexing,
        file=file,
    )

    issn_1, issn_2 = extract_issn_parts(issn)

    result = search_source_for_issn(dataset, issn_1)

    if result is not None:
        new_publication_name = get_attribute(result, "Title")
        new_publisher_name = get_attribute(result, "Publisher", old_publisher_name)
        print_results(
            new_publication_name=new_publication_name,
            new_publisher_name=new_publisher_name,
            file=file,
        )
        update_df(row, new_df, new_publication_name, new_publisher_name, old_indexing)
        return True

    if issn_2:
        result = search_source_for_issn(dataset, issn_2)
        if result is not None:
            new_publication_name = get_attribute(result, "Title")
            new_publisher_name = get_attribute(result, "Publisher", old_publisher_name)
            print_results(
                new_publication_name=new_publication_name,
                new_publisher_name=new_publisher_name,
                file=file,
            )
            update_df(
                row, new_df, new_publication_name, new_publisher_name, old_indexing
            )
            return True

    print("Not Found!", file=file)

    return False


def main():
    df = read_source_file("files/temp_results/scopus_publications.csv")
    new_df = df.copy()

    dataset_df = load_dataset("files/input/wos-core_SCIE 2024-April-15.csv")

    count = 0

    with open("files/logs/wos_results.txt", "w+", encoding="utf-8") as f:
        for index, row in df.iterrows():
            print("==================================================", file=f)
            r = process_row(row, dataset_df, new_df, f)
            if r:
                count += 1
        print(count, file=f)

    new_df.to_csv("files/temp_results/wos_publications.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
