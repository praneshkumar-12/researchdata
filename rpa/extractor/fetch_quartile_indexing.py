import csv


def get_scopus_journals():
    scopus_journals = {}

    with open("scopus-dataset.csv", encoding="utf-8") as scopus_file:
        scopus_reader = csv.reader(scopus_file)

        for row in scopus_reader:
            scopus_journals[row[0]] = row[1]

    return scopus_journals


def update_dataset(scopus_journals):
    content_to_write = []

    with open("journal_ranking_data.csv", "r", encoding="utf-8") as journal_file:
        journal_reader = csv.reader(journal_file)

        for row in journal_reader:
            # print(row[1])
            publisher = (
                scopus_journals.get(row[1])
                if scopus_journals.get(row[1]) is not None
                else []
            )
            if row[1] in scopus_journals and row[3] in publisher:
                content_to_write.append(
                    [row[0], row[1], row[2], row[3], row[4] + f" | Scopus"]
                )
            else:
                content_to_write.append([row[0], row[1], row[2], row[3], row[4]])

    with open(
        "wos-scopus-dataset.csv", "w", encoding="utf-8", newline=""
    ) as updated_file:
        updated_writer = csv.writer(updated_file)

        updated_writer.writerows(content_to_write)


def create_combined_dataset_indexing_quartile():
    scopus_journals = get_scopus_journals()
    update_dataset(scopus_journals)
