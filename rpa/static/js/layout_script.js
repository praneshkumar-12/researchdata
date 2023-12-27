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

    for(var k=0; k<searchTerms.length;k++){
        if (rowstring.includes(searchTerms[k].toUpperCase())){
            found = found && true;
        }
        else{
            found = found && false;
            break;
        }
    }
        tr[i].style.display = found ? "" : "none";
    }
}

function lookForEmptySearch(){
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById("searchBox");
    filter = input.value.toUpperCase();
    table = document.getElementById("tableBody");
    tr = table.getElementsByTagName("tr");

    if (filter === ""){

    for (i = 0; i < tr.length; i++) {
        tr[i].style.display = "";
    }
}
}

setInterval(lookForEmptySearch, 100);