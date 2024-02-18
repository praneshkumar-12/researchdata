import csv
import os
import json
from habanero import Crossref
import requests
import logging
from unidecode import unidecode
import re
import jellyfish
from rpa.extractor.fetch_quartile_indexing import (
    create_combined_dataset_indexing_quartile,
)

HEADER_WRITTEN = False
SKIP = False

logging.basicConfig(
    filename="extractor.log", format="%(asctime)s %(message)s", filemode="w"
)
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

somefile = open("something.txt", "a")

database_fields = {
    "uniqueid": None,
    "title": None,
    "start_academic_month": None,
    "start_academic_year": None,
    "end_academic_month": None,
    "end_academic_year": None,
    "first_author": None,
    "second_author": None,
    "third_author": None,
    "other_authors": None,
    "is_student_author": None,
    "student_name": None,
    "student_batch": None,
    "specification": None,
    "publication_type": None,
    "publication_name": None,
    "publisher": None,
    "year_of_publishing": None,
    "month_of_publishing": None,
    "volume": None,
    "page_number": None,
    "indexing": None,
    "quartile": None,
    "citation": None,
    "doi": None,
    "fpp": None,
    "url": None,
    "ISSN": None,
}


def dump_json(file_contents, file_name, rewrite=True):
    mode = "w" if rewrite else "a"
    with open(file_name, mode) as dump_file:
        json.dump(file_contents, dump_file)

    return True


def load_json(file_name):
    with open(file_name, "r") as load_file:
        return json.load(load_file)


def asciify(string):
    return (
        unidecode(string, errors="replace", replace_str=" ")
        .encode("ascii")
        .decode("ascii")
    )


def match_string(string1, string2):
    match = jellyfish.jaro_winkler_similarity(string1, string2, long_tolerance=True)

    return match


def remove_special_chars(string):
    return "".join([ch for ch in string if ch.isalnum()])


def compare_titles(string1, string2):
    if remove_special_chars(
        asciify(string1).lower().strip().replace(" ", "")
    ) in remove_special_chars(asciify(string2).lower().strip().replace(" ", "")):
        return True
    return False


def fetch_data_crossref(title):
    cr = Crossref()

    fetched_json = cr.works(query=title, limit=1)

    logging.info(f"Fetched JSON data from Crossref for {title}")

    dump_json(fetched_json["message"]["items"][0], "temp.json")

    return fetched_json["message"]["items"][0]


def validate_fetched_data(title, fetched_data):
    original_title = title
    scrape_data = fetched_data

    scraped_title = scrape_data["title"][0]

    print(
        asciify(scraped_title),
        asciify(original_title),
        match_string(asciify(scraped_title), asciify(original_title)),
        "\n",
        file=somefile,
    )
    if not compare_titles(asciify(scraped_title), asciify(original_title)):
        logging.critical(f"Cannot validate data for {original_title}")
        print(f"Cannot validate data for {original_title}")
        return False

    logging.info(f"Validated data for {original_title}")
    return True


def extract_from_json(fetched_data):
    authors = fetched_data.get("author")

    author_list = []

    if authors is None:
        database_fields["first_author"] = "NULL"
        database_fields["second_author"] = "NULL"
        database_fields["third_author"] = "NULL"
        database_fields["other_authors"] = "NULL"
        logging.critical("Author not found, but continuing...")
    else:
        length = len(authors)
        for idx in range(length):
            if fetched_data["author"][idx].get("given") is not None:
                author_list.append(
                    fetched_data["author"][idx]["given"]
                    + " "
                    + fetched_data["author"][idx]["family"]
                )

        if len(author_list) == 1:
            database_fields["first_author"] = author_list[0]
            database_fields["second_author"] = "NULL"
            database_fields["third_author"] = "NULL"
            database_fields["other_authors"] = "NULL"
        elif len(author_list) == 2:
            database_fields["first_author"] = author_list[0]
            database_fields["second_author"] = author_list[1]
            database_fields["third_author"] = "NULL"
            database_fields["other_authors"] = "NULL"
        elif len(author_list) == 3:
            database_fields["first_author"] = author_list[0]
            database_fields["second_author"] = author_list[1]
            database_fields["third_author"] = author_list[2]
            database_fields["other_authors"] = "NULL"
        else:
            database_fields["first_author"] = author_list[0]
            database_fields["second_author"] = author_list[1]
            database_fields["third_author"] = author_list[2]
            database_fields["other_authors"] = ", ".join(author_list[3:])

    if "article" in database_fields["specification"]:
        database_fields["publication_type"] = "Journal"
    elif "inbook" in database_fields["specification"]:
        database_fields["publication_type"] = "Book Chapter"
    elif "incollection" in database_fields["specification"]:
        database_fields["publication_type"] = "Conference"
    elif "inproceeding" in database_fields["specification"]:
        database_fields["publication_type"] = "Conference"

    database_fields["year_of_publishing"] = fetched_data["published"]["date-parts"][0][
        0
    ]

    database_fields["month_of_publishing"] = (
        fetched_data["published"]["date-parts"][0][1]
        if len(fetched_data.get("published").get("date-parts")[0]) > 1
        else None
    )

    database_fields["page_number"] = (
        fetched_data["page"] if fetched_data.get("page") is not None else None
    )

    database_fields["citation"] = fetched_data["is-referenced-by-count"]

    database_fields["url"] = fetched_data["URL"]

    database_fields["ISSN"] = (
        " ".join(fetched_data["ISSN"]) if fetched_data.get("ISSN") is not None else None
    )

    database_fields["uniqueid"] = (
        str(database_fields["start_academic_year"])
        + str(database_fields["start_academic_month"])
        + "".join(letter for letter in database_fields["doi"] if letter.isalnum())
    )


def set_title(fetched_data):
    database_fields["title"] = asciify(fetched_data["title"][0])
    logging.info(f"Set title as {database_fields['title']}")


def set_academic_year(start_month, start_year, end_month, end_year):
    database_fields["start_academic_month"] = start_month
    database_fields["start_academic_year"] = start_year
    database_fields["end_academic_month"] = end_month
    database_fields["end_academic_year"] = end_year


def get_doi(fetched_data):
    database_fields["doi"] = asciify(fetched_data["DOI"])
    logging.info(f"Set title as {database_fields['doi']}")
    return database_fields["doi"]


def get_bibtex_update(doi):
    base_url = (
        "https://api.crossref.org/works/" + str(doi) + "/transform/application/x-bibtex"
    )
    response = requests.request("GET", url=base_url)

    logging.info(
        f"Fetched BibTeX data for {doi} with response code {response.status_code}"
    )

    if response.status_code == 200:
        content = response.text

        specification = re.findall(r"@([\S]+){", content)
        volume_number = re.findall(r"volume={([\d]+)}", content)

        database_fields["specification"] = (
            asciify(specification[0]) if specification else "NULL"
        )
        database_fields["volume"] = (
            asciify(volume_number[0]) if volume_number else "NULL"
        )
        logging.info(f"Updated specification and volume number for DOI: {doi}")

        return True

    else:
        print("Uh-Oh! Some error occured in BibTex. ")

        logging.critical(
            f"Cannot fetch BibTex for DOI: {doi} Response code: {response.status_code}"
        )

        return False


def get_publication_name(fetched_data):
    try:
        publication_name = fetched_data["container-title"][0]
        logging.info("Fetched publication name")
    except KeyError:
        publication_name = "NULL"
        logging.critical("Cannot fetch publication name, skipping record!")
        skip_record()
        return "-999"

    database_fields["publication_name"] = asciify(publication_name)
    logging.info("Set publication name")

    return database_fields["publication_name"]


def get_publisher(fetched_data):
    publisher = fetched_data["publisher"]

    logging.info("Fetched publisher")

    database_fields["publisher"] = asciify(publisher)
    logging.info("Set publisher")

    return database_fields["publisher"]


def get_indexing_quartile_data(publisher, publication_name):
    with open("wos-scopus-dataset.csv", "r", encoding="utf-8") as dataset_file:
        reader = csv.reader(dataset_file)

        indexing_data = []

        quartile = ""

        for row in reader:
            if (
                "Scopus" in asciify(row[4])
                and publication_name == asciify(row[1])
                and asciify(row[3]) in publisher
            ):
                indexing_data.append("Scopus")
                logging.info("Paper found in Scopus")
            elif (
                "Science Citation Index" in asciify(row[4])
                and publication_name == asciify(row[1])
                and asciify(row[3]) in publisher
            ):
                indexing_data.append("Web of Sciences")

            if publication_name == asciify(row[1]) and asciify(row[3]) in publisher:
                quartile = asciify(row[2])

        if "Scopus" not in indexing_data:
            logging.debug("Paper not in Scopus")
        if "Web of Sciences" not in indexing_data:
            logging.debug("Paper not in Web of Sciences")
        if not quartile:
            quartile = "NULL"
            logging.debug("Quartile not found")

    # with open("scopus-dataset.csv", "r", encoding="utf-8") as scopus_dataset:
    #     scopus_reader = csv.reader(scopus_dataset)

    #     for scopus_data in scopus_reader:
    #         if asciify(scopus_data[0]) == publication_name and asciify(scopus_data[1]) in publisher:
    #             logging.info("Paper found in Scopus")
    #             indexing_data.append("Scopus")
    #             break
    #     else:
    #         logging.debug("Paper not in Scopus")

    # with open("journal_ranking_data.csv","r", encoding="utf-8") as wos_dataset:

    #     wos_reader = csv.reader(wos_dataset)

    #     for wos_data in wos_reader:
    #         if asciify(wos_data[1]) == publication_name and asciify(wos_data[3]) in publisher and "Science Citation Index".lower() in asciify(wos_data[4]):
    #             logging.info("Paper found in Web of Sciences")
    #             indexing_data.append("Web of Sciences")
    #     else:
    #         logging.debug("Paper not in Web of Sciences")

    # for wos_data in wos_reader:
    #     if asciify(wos_data[1]) == publication_name and asciify(wos_data[3]) in publisher:
    #         quartile = asciify(wos_data[2])
    #         database_fields["quartile"] = quartile
    #         logging.info("Quartile found and set")
    # else:
    #     logging.debug("Quartile not found")

    database_fields["indexing"] = " ".join(indexing_data) if indexing_data else "NULL"
    logging.info("Indexing set")
    database_fields["quartile"] = quartile
    logging.info("Quartile set")


def convert_to_csv():
    with open("research-data-new-refactored.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file)

        content_to_write = []
        for key, value in database_fields.items():
            if (not value) or (value is not None and "NULL" == value):
                logging.warning(f"Value for {key} not found")
                content_to_write.append("NULL")
            else:
                logging.warning(f"Value for {key} found")
                content_to_write.append(asciify(str(value)))

        writer.writerow(content_to_write)


def init_csv_header():
    global HEADER_WRITTEN
    if not HEADER_WRITTEN:
        with open("research-data-new-refactored.csv", "w", newline="") as init_file:
            init_writer = csv.writer(init_file)
            init_writer.writerow([key for key in database_fields.keys()])
            HEADER_WRITTEN = True
        init_file.close()

        create_combined_dataset_indexing_quartile()


def skip_record():
    global SKIP
    SKIP = True


def reset_skip():
    global SKIP
    SKIP = False


def return_list():
    content_to_write = {}
    for key, value in database_fields.items():
        if (not value) or (value is not None and "NULL" == value):
            logging.warning(f"Value for {key} not found")
            content_to_write[key] = "NULL"
        else:
            logging.warning(f"Value for {key} found")
            content_to_write[key] = asciify(str(value))

    return content_to_write


def get_title(doi):
    base_url = (
        "https://api.crossref.org/works/" + str(doi) + "/transform/application/x-bibtex"
    )
    response = requests.request("GET", url=base_url)

    if response.status_code == 200:
        content = response.text
        title = re.findall(r"title={(.+)}, v", content)
        if not title:
            return False
        return title[0]
    else:
        return ""


def main(title, ay):
    create_combined_dataset_indexing_quartile()
    fetched_data = fetch_data_crossref(title)
    if not validate_fetched_data(title, fetched_data):
        return False
    ay_split = ay.replace(" -", "").split(" ")
    print(ay_split)
    set_academic_year(ay_split[0], ay_split[1], ay_split[2], ay_split[3])
    set_title(fetched_data)
    doi = get_doi(fetched_data)
    get_bibtex_update(doi)
    publication_name = get_publication_name(fetched_data)
    if SKIP:
        reset_skip()
        return None
    publisher = get_publisher(fetched_data)
    get_indexing_quartile_data(publisher, publication_name)
    extract_from_json(fetched_data)
    return return_list()


# main('''27.	Naveen, S., Mayank Singh, and S. Karthika. "Swear Words Replacement Suggestion System." In ICT Analysis and Applications, pp. 271-280. Springer, Singapore, 2022. https://doi.org/10.1007/978-981-16-5655-2_26''')

# content = ""

# for row in content.split("\n"):
#     main(row)
