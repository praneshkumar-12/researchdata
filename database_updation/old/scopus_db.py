import pandas as pd


df = pd.read_csv("publications.csv", encoding="utf-8")
new_df = df.copy()


source_files = [
    r"F:\researchdata-enh\researchdata\database_updation\resources-csv\accepted-titles-feb-2024.csv",
    r"F:\researchdata-enh\researchdata\database_updation\resources-csv\discontinued-feb-2024.csv",
    r"F:\researchdata-enh\researchdata\database_updation\resources-csv\scopus-book-series.csv",
    r"F:\researchdata-enh\researchdata\database_updation\resources-csv\scopus-sources-oct-2023.csv",
    r"F:\researchdata-enh\researchdata\database_updation\resources-csv\serial-conference-proceedings.csv",
]

source_readers = [
    pd.read_csv(source_file, encoding="utf-8") for source_file in source_files
]
count = 0

pd.set_option("display.max_colwidth", None)

file = open("results.txt", "w+")

for index, row in df.iterrows():
    print("==================================================", file=file)
    issn = str(row["ISSN"])
    title = str(row["title"])
    old_publication_name = str(row["publication_name"])
    old_publisher = str(row["publisher"])
    # print(row['indexing'], pd.isna(row['indexing']))
    print("ISSN:", issn, file=file)
    print("Title:", title, file=file)
    print("Old Publication:", old_publication_name, file=file)
    print("Old Publisher:", old_publisher, file=file)

    issn_split = issn.split(" ")
    if len(issn_split) == 2:
        issn_1 = issn_split[0].replace("-", "").lstrip("0")
        issn_2 = issn_split[1].replace("-", "").lstrip("0")
    else:
        issn_1 = issn_split[0].replace("-", "")
        issn_2 = None

    for source_reader in source_readers:
        result_found = False  # Flag to track if result found in this source_reader

        # Check for ISSN
        if issn_1:
            result = source_reader[
                source_reader["PrintISSN"].str.contains(issn_1, na=False)
            ]
            if not result.empty:
                new_publication_name = result["Title"]
                splitted_name = str(new_publication_name).split(" ")
                if splitted_name[0].isnumeric():
                    new_publication_name = str(result["Title"])[
                        len(splitted_name[0]) : str(new_publication_name).index("Name:")
                    ].strip()

                new_publisher_name = result.get("Publisher", old_publisher)
                splitted_publisher = str(new_publisher_name).split(" ")
                if splitted_publisher[0].isnumeric():
                    new_publisher_name = str(result["Publisher"])[
                        len(splitted_publisher[0]) : str(new_publisher_name).index(
                            "Name:"
                        )
                    ].strip()
                print("Title:", title, file=file)
                print("Old:", old_publication_name, file=file)
                print("New:", new_publication_name, file=file)
                print("Result found in ISSN1 Print ISSN", file=file)
                count += 1
                new_df.at[index, "publication_name"] = new_publication_name
                result_found = True
                if "Scopus" in str(row["indexing"]):
                    break
                new_df.at[index, "indexing"] = str("Scopus")
                new_df.at[index, "publisher"] = new_publisher_name
                # elif str(row['indexing']).lower() == "null" or str(row['indexing']).lower() == "none" or pd.isna(row['indexing']):
                #     new_df.at[index, 'indexing'] = "Scopus"
                # else:
                #     new_df.at[index, 'indexing'] = str(row['indexing']) + str(", Scopus")
                break
            else:
                result = source_reader[
                    source_reader["EISSN"].str.contains(issn_1, na=False)
                ]
                if not result.empty:
                    new_publication_name = result["Title"]
                    splitted_name = str(new_publication_name).split(" ")
                    if splitted_name[0].isnumeric():
                        new_publication_name = str(result["Title"])[
                            len(splitted_name[0]) : str(new_publication_name).index(
                                "Name:"
                            )
                        ].strip()

                    new_publisher_name = result.get("Publisher", old_publisher)
                    splitted_publisher = str(new_publisher_name).split(" ")
                    if splitted_publisher[0].isnumeric():
                        new_publisher_name = str(result["Publisher"])[
                            len(splitted_publisher[0]) : str(new_publisher_name).index(
                                "Name:"
                            )
                        ].strip()
                    print("Title:", title, file=file)
                    print("Old:", old_publication_name, file=file)
                    print("New:", new_publication_name, file=file)
                    print("Result found in ISSN1 E ISSN", file=file)
                    count += 1
                    new_df.at[index, "publication_name"] = new_publication_name
                    result_found = True
                    if "Scopus" in str(row["indexing"]):
                        break
                    new_df.at[index, "indexing"] = str("Scopus")
                    new_df.at[index, "publisher"] = result.get(
                        "Publisher", old_publisher
                    )
                    # elif str(row['indexing']).lower() == "null" or str(row['indexing']).lower() == "none" or pd.isna(row['indexing']):
                    #     new_df.at[index, 'indexing'] = "Scopus"
                    # else:
                    #     new_df.at[index, 'indexing'] = str(row['indexing']) + str(", Scopus")
                    break

        # If ISSN lookup didn't find anything, check for ISSN2
        if not result_found and issn_2:
            result = source_reader[
                source_reader["PrintISSN"].str.contains(issn_2, na=False)
            ]
            if not result.empty:
                new_publication_name = result["Title"]
                splitted_name = str(new_publication_name).split(" ")
                if splitted_name[0].isnumeric():
                    new_publication_name = str(result["Title"])[
                        len(splitted_name[0]) : str(new_publication_name).index("Name:")
                    ].strip()

                new_publisher_name = result.get("Publisher", old_publisher)
                splitted_publisher = str(new_publisher_name).split(" ")
                if splitted_publisher[0].isnumeric():
                    new_publisher_name = str(result["Publisher"])[
                        len(splitted_publisher[0]) : str(new_publisher_name).index(
                            "Name:"
                        )
                    ].strip()
                print("Title:", title, file=file)
                print("Old:", old_publication_name, file=file)
                print("New:", new_publication_name, file=file)
                print("Result found in ISSN2 Print ISSN", file=file)
                count += 1
                new_df.at[index, "publication_name"] = new_publication_name
                result_found = True
                if "Scopus" in str(row["indexing"]):
                    break
                new_df.at[index, "indexing"] = str("Scopus")
                new_df.at[index, "publisher"] = result.get("Publisher", old_publisher)
                # elif str(row['indexing']).lower() == "null" or str(row['indexing']).lower() == "none" or pd.isna(row['indexing']):
                #     new_df.at[index, 'indexing'] = "Scopus"
                # else:
                #     new_df.at[index, 'indexing'] = str(row['indexing']) + str(", Scopus")
                break
            else:
                result = source_reader[
                    source_reader["EISSN"].str.contains(issn_2, na=False)
                ]
                if not result.empty:
                    new_publication_name = result["Title"]
                    splitted_name = str(new_publication_name).split(" ")
                    if splitted_name[0].isnumeric():
                        new_publication_name = str(result["Title"])[
                            len(splitted_name[0]) : str(new_publication_name).index(
                                "Name:"
                            )
                        ].strip()

                    new_publisher_name = result.get("Publisher", old_publisher)
                    splitted_publisher = str(new_publisher_name).split(" ")
                    if splitted_publisher[0].isnumeric():
                        new_publisher_name = str(result["Publisher"])[
                            len(splitted_publisher[0]) : str(new_publisher_name).index(
                                "Name:"
                            )
                        ].strip()
                    print("Title:", title, file=file)
                    print("Old:", old_publication_name, file=file)
                    print("New:", new_publication_name, file=file)
                    print("Result found in ISSN2 E ISSN", file=file)
                    count += 1
                    new_df.at[index, "publication_name"] = new_publication_name
                    result_found = True
                    if "Scopus" in str(row["indexing"]):
                        break
                    new_df.at[index, "indexing"] = str("Scopus")
                    new_df.at[index, "publisher"] = result.get(
                        "Publisher", old_publisher
                    )
                    # elif str(row['indexing']).lower() == "null" or str(row['indexing']).lower() == "none" or pd.isna(row['indexing']):
                    #     new_df.at[index, 'indexing'] = "Scopus"
                    # else:
                    #     new_df.at[index, 'indexing'] = str(row['indexing']) + str(", Scopus")
                    break

    else:
        if not result_found:
            print("Not found!", file=file)


print(count, file=file)
file.close()

new_df.to_csv("new_publication.csv", index=False, encoding="utf-8")
