function getIndexByKey(key) {
    var table = document.getElementById("publicationTable");
    for (var i = 0, row; row = table.rows[i]; i++) {
        // Assuming the first cell contains the field name
        var fieldName = row.cells[0].textContent.trim();
        if (fieldName === key) {
            // Return the index of the row
            return i;
        }
    }
    // If key not found, return -1 or appropriate error handling
    return -1;
}

function getKeyByIndex(index) {
    var table = document.getElementById("publicationTable");
    for (var i = 0, row; row = table.rows[i]; i++) {
        // Assuming the first cell contains the field name
        var fieldName = row.cells[0].textContent.trim();
        if (i === index) {
            // Return the index of the row
            return fieldName;
        }
    }
    // If key not found, return ""
    return "";
}

function convertToSnakeCase(key){
    return key.toLowerCase().replace(/\s+/g, '_');
}