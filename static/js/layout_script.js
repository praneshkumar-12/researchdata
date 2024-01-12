function filterTable() {
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById("searchBox");
    filter = input.value.toUpperCase();
    if (filter === "") return filter
    table = document.getElementById("tableBody");
    tr = table.getElementsByTagName("tr");

    var searchTerms = filter.split(" ").filter(term => term.trim() !== "");

    for (i = 0; i < tr.length; i++) {
        var rowstring = "";
        for (j = 0; j < tr[i].cells.length; j++) {
            td = tr[i].cells[j];
            if (td) {
                txtValue = td.textContent || td.innerText;
                rowstring = rowstring.concat(txtValue);
            }
        }
        rowstring = rowstring.toUpperCase();

        // console.log(rowstring);

        found = true;

        for (var k = 0; k < searchTerms.length; k++) {
            if (rowstring.includes(searchTerms[k].toUpperCase())) {
                found = found && true;
            } else {
                found = found && false;
                break;
            }
        }
        tr[i].style.display = found ? "" : "none";
    }
}

function lookForEmptySearch() {
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById("searchBox");
    filter = input.value.toUpperCase();
    table = document.getElementById("tableBody");
    tr = table.getElementsByTagName("tr");

    if (filter === "") {

        for (i = 0; i < tr.length; i++) {
            tr[i].style.display = "";
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('id_uniqueid').disabled = true;
    document.getElementById('id_title').disabled = true;
    document.getElementById('id_AY').disabled = true;
    document.getElementById('id_first_author').disabled = true;
    document.getElementById('id_second_author').disabled = true;
    document.getElementById('id_third_author').disabled = true;
    document.getElementById('id_other_authors').disabled = true;
    document.getElementById('id_is_student_author').disabled = true;
    document.getElementById('id_student_name').disabled = true;
    document.getElementById('id_student_batch').disabled = true;
    document.getElementById('id_specification').disabled = true;
    document.getElementById('id_publication_type').disabled = true;
    document.getElementById('id_publication_name').disabled = true;
    document.getElementById('id_publisher').disabled = true;
    document.getElementById('id_year_of_publishing').disabled = true;
    document.getElementById('id_month_of_publishing').disabled = true;
    document.getElementById('id_volume').disabled = true;
    document.getElementById('id_page_number').disabled = true;
    document.getElementById('id_indexing').disabled = true;
    document.getElementById('id_quartile').disabled = true;
    document.getElementById('id_citation').disabled = true;
    document.getElementById('id_doi').disabled = false;
    document.getElementById('id_front_page_path').disabled = true;
    document.getElementById('id_url').disabled = true;
    document.getElementById('id_issn').disabled = true;
    document.getElementById('fetchData').disabled = false;
});

function edit_before_verify(uniqueId) {
    var row = document.querySelector('#tableBody tr[data-uniqueid="' + uniqueId + '"]');
    console.log(row);

    if (row) {
        Array.from(row.cells).forEach(function(cell, index) {
            if (index === findHeaderIndex("Is Student Author")) {
                var selectElement = document.createElement('select');
                selectElement.id = 'studentAuthor';
                selectElement.name = 'SA';
                var optionElement = document.createElement('option');
                optionElement.value = "Yes";
                optionElement.textContent = "Yes";
                selectElement.appendChild(optionElement);
                var optionElement = document.createElement('option');
                optionElement.value = "No";
                optionElement.textContent = "No";
                selectElement.appendChild(optionElement);
                cell.innerHTML = '';
                cell.appendChild(selectElement);
            }
            if (cell.textContent.trim() === 'NULL' && index != findHeaderIndex("FPP")) {
                var inputElement = document.createElement('input');
                inputElement.type = 'text';
                inputElement.value = cell.textContent.trim();
                cell.innerHTML = '';
                cell.appendChild(inputElement);
            } else if (index === findHeaderIndex("FPP")) {
                console.log("FPP");
            }
        })
        var btnelts = document.getElementsByClassName('verify-btn');

        var btnlen = btnelts.length
        for (var i = 0; i < btnlen; i++) {
            // console.log(btnelts[i])
            if (btnelts[i].value == uniqueId) {
                var btn = btnelts[i];
                break;
            }
        }
        btn.innerText = "Validate";
        btn.setAttribute('onclick', 'verify(this.value)');
    }
}

function disableFetch() {
    fetch_btn = document.getElementById("fetchData");
    fetch_btn.disabled = true;
    fetch_btn.classList.remove("scrape-btn");
    fetch_btn.classList.add("scraped-btn");
    console.log("Changing class to disabled");
    document.getElementById('fetchData').innerHTML = "Fetching...";
}

function enableFetch() {
    document.getElementById('fetchData').disabled = false;
    document.getElementById('fetchData').innerHTML = "Submit";
    console.log("Changing class to enabled");
    fetch_btn = document.getElementById("fetchData");
    fetch_btn.disabled = false;
    fetch_btn.classList.remove("scraped-btn");
    fetch_btn.classList.add("scrape-btn");
}

function enableFetchNoResponse() {
    document.getElementById('fetchData').disabled = false;
    document.getElementById('fetchData').innerHTML = "Fetch";
    console.log("Changing class to enabled");
    fetch_btn = document.getElementById("fetchData");
    fetch_btn.disabled = false;
    fetch_btn.classList.remove("scraped-btn");
    fetch_btn.classList.add("scrape-btn");
}

function formatDate(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function downloadCSV() {
    var csv_data = [];
    var rows = document.getElementsByTagName('tr');

    var counter = 1;

    var row_content = "";

    for (var i = 0; i < rows.length; i++) { // Exclude the last row
        if (i === rows.length - 1) {
            row_content = rows[i].querySelectorAll('td,th');
            content = row_content[1].innerHTML;
            if (content.includes("input")) {
                continue;
            }
        }
        // Check if the row is visible (style.display is not "none")
        if (window.getComputedStyle(rows[i]).display !== 'none') {
            var cols = rows[i].querySelectorAll('td,th');
            var csvrow = [];

            for (var j = 0; j < cols.length - 1; j++) {
                // console.log(cols[j].innerHTML)
                // Add automatic serial numbers for the first row
                if (j === findHeaderIndex("Verification") || i === findHeaderIndex("Actions") || i === findHeaderIndex("Faculty Verification Status")) {
                    continue;
                }

                if (window.getComputedStyle(cols[j]).display !== 'none') {
                    // Add double quotes to the 8th column (index 7)

                    if (i === 0 && j === 0) {
                        csvrow.push("Serial Number");
                    } else {

                        if (i !== 0 && (j === findHeaderIndex("URL") || j === findHeaderIndex("FPP"))) {

                            cellContent = cols[j].getElementsByTagName("a");

                            if (cellContent.length != 0) {
                                console.log(cellContent);
                                cellContent = cellContent[0].getAttribute("href");
                            } else {
                                cellContent = 'NULL';
                            }
                            csvrow.push('"' + cellContent + '"');
                            continue;
                        }
                        if (i !== 0 && j === 0) {
                            csvrow.push(counter);
                            counter += 1;
                            continue;
                        }
                        // Add double quotes to the 8th column (index 7)

                        csvrow.push('"' + cols[j].innerHTML + '"');
                    }
                }
            }

            csv_data.push(csvrow.join(","));
        }
    }

    csv_data = csv_data.join('\n');
    downloadCSVFile(csv_data);
}

function downloadCSVFile(csv_data) {
    // Create CSV file object and feed
    // our csv_data into it
    CSVFile = new Blob([csv_data], {
        type: "text/csv"
    });

    // Create to temporary link to initiate
    // download process
    var temp_link = document.createElement('a');

    var currentDate = new Date();
    var formattedDate = formatDate(currentDate);

    // Download csv file
    temp_link.download = "research_papers_" + formattedDate + ".csv";
    var url = window.URL.createObjectURL(CSVFile);
    temp_link.href = url;

    // This link should not be displayed
    temp_link.style.display = "none";
    document.body.appendChild(temp_link);

    // Automatically click the link to
    // trigger download
    temp_link.click();
    document.body.removeChild(temp_link);
}

function lookForEmptySearch() {
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById("searchBox");
    filter = input.value.toUpperCase();
    table = document.getElementById("tableBody");
    tr = table.getElementsByTagName("tr");

    if (filter === "") {

        for (i = 0; i < tr.length; i++) {
            tr[i].style.display = "";
        }
    }
}

function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("mytable");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 2); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }



        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function sortTablenum(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("mytable");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 2); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (Number(x.innerHTML) > Number(y.innerHTML)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (Number(x.innerHTML) < Number(y.innerHTML)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }



        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function applyFilter() {
    var matchesAY = selectedAY === "all" || (AYCell ? AYCell.innerHTML.includes(selectedAY) : false);
    var scopusCheckbox = document.querySelector('input[name="scopus"]');
    var webOfSciencesCheckbox = document.querySelector('input[name="webOfSciences"]');
    var quartileSelect = document.getElementById("quartile");
    var AYSelect = document.getElementById("AY");
    var table = document.getElementById("mytable");
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var indexingCell = rows[i].getElementsByTagName("td")[findHeaderIndex("Indexing")]; // Assuming indexing is at index 19, adjust if needed
        var quartileCell = rows[i].getElementsByTagName("td")[findHeaderIndex("Quartile")]; // Assuming quartile is at index 20, adjust if needed
        var AYCell = rows[i].getElementsByTagName("td")[findHeaderIndex("Academic Year")]; // Assuming Academic Year is at index 3, adjust if needed

        var scopusChecked = scopusCheckbox.checked;
        var webOfSciencesChecked = webOfSciencesCheckbox.checked;
        var quartileSelected = quartileSelect.value;
        var selectedAY = AYSelect.value;

        var containsWebOfScience = indexingCell ? indexingCell.innerHTML.toLowerCase().includes("web of science") : false;
        var containsScopus = indexingCell ? indexingCell.innerHTML.toLowerCase().includes("scopus") : false;
        var matchesQuartile = quartileCell ? quartileCell.innerHTML.toLowerCase().includes(quartileSelected) : false;
        var matchesAY = selectedAY === "all" || (AYCell ? AYCell.innerHTML.includes(selectedAY) : false);

        var shouldBeHidden = false;

        if (quartileSelected !== "all") { // Check if "All Quartiles" is not selected
            if (
                (webOfSciencesChecked && !containsWebOfScience) ||
                (scopusChecked && !containsScopus) ||
                (quartileSelected !== "" && !matchesQuartile) ||
                !matchesAY
            ) {
                shouldBeHidden = true;
            }
        } else {
            // Show all rows when "All Quartiles" is selected
            if (webOfSciencesChecked && !containsWebOfScience) {
                shouldBeHidden = true;
            }
            if (scopusChecked && !containsScopus) {
                shouldBeHidden = true;
            }
            if (!matchesAY) {
                shouldBeHidden = true;
            }
        }

        if (shouldBeHidden) {
            rows[i].classList.add("hidden");
        } else {
            rows[i].classList.remove("hidden");
        }
    }
}

function sortTableByQuartile() {
    var table = document.getElementById("mytable");
    var rows = Array.from(table.getElementsByTagName("tr"));

    rows.sort(function(a, b) {
        var aValue = a.getElementsByTagName("td")[findHeaderIndex("Quartile")].innerHTML.toLowerCase(); // Adjust index if needed
        var bValue = b.getElementsByTagName("td")[findHeaderIndex("Quartile")].innerHTML.toLowerCase(); // Adjust index if needed
        return aValue.localeCompare(bValue);
    });

    // Clear the table
    table.innerHTML = "";

    // Append sorted rows
    for (var i = 0; i < rows.length; i++) {
        table.appendChild(rows[i]);
    }
}

function upload(uniqueid) {
    window.open("/rpa/auth/upload/" + uniqueid, "_blank");
}

function findHeaderIndex(headerText) {
    // Get the table element by its ID
    var table = document.getElementById("mytable");

    // Check if the table exists
    if (table) {
        // Get the first row (thead) of the table
        var thead = table.querySelector('thead');

        // Check if thead exists
        if (thead) {
            // Find all th elements in the first row
            var headerCells = thead.querySelectorAll('th');

            // Loop through each header cell to find the index of the one with the specified text content
            for (var i = 0; i < headerCells.length; i++) {
                if (headerCells[i].textContent.trim() === headerText.trim()) {
                    // Return the index if a match is found
                    return i;
                }
            }
        }
    }

    // Return -1 if the table or header is not found
    return -1;
}


document.getElementById('quartile').addEventListener('change', function() {
    sortTableByQuartile();
    applyFilter();
});



setInterval(lookForEmptySearch, 100);