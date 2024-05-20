const publications = document.querySelectorAll('.publication');
const recordsPerPage = 8;
const totalPublications = publications.length;
let currentPage = 0;

function showPublication(page) {
    const startIndex = page * recordsPerPage;
    const endIndex = Math.min(startIndex + recordsPerPage, totalPublications);
    
    publications.forEach((publication, index) => {
        if (index >= startIndex && index < endIndex) {
            publication.style.display = 'block';
        } else {
            publication.style.display = 'none';
        }
    });
}

function showNext() {
    if (currentPage < Math.ceil(totalPublications / recordsPerPage) - 1) {
        currentPage++;
        showPublication(currentPage);
        updatePageNumber();
    }
}

function showPrev() {
    if (currentPage > 0) {
        currentPage--;
        showPublication(currentPage);
        updatePageNumber();
    }
}

function updatePageNumber() {
    document.getElementById('pageNumberTop').innerText = `Page ${currentPage + 1} of ${Math.ceil(totalPublications / recordsPerPage)}`;
    document.getElementById('pageNumberBottom').innerText = `Page ${currentPage + 1} of ${Math.ceil(totalPublications / recordsPerPage)}`;
}

// Initially show the first page of publications and update page number
showPublication(currentPage);
updatePageNumber();

// Function to filter publications by title
function filterPublications() {
    var nav_elts = document.getElementsByClassName("navigation");

    for (var i = 0; i < nav_elts.length; i++) {
        nav_elts[i].style.display = "none";
    }

    var input, filter, publications, publication, title, i, txtValue;
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();
    if (filter === "") return filter
    publications = document.getElementsByClassName('publication');
    var searchTerms = filter.split(" ").filter(term => term.trim() !== "");


    var visible = [];
    var invisible = [];

    for(var i = 0; i < publications.length; i++){
        var publication = publications[i];
        title = publication.getElementsByTagName("a")[0].innerHTML.toUpperCase();
        var found = true;        
        for (var k = 0; k < searchTerms.length; k++) {
            if (title.includes(searchTerms[k].toUpperCase())){
                found = found && true;
            } else {
                found = found && false;
                break;
            }
        }


        if (found){
            visible.push(publication);
        }

    }

    for(var i = 0; i < publications.length; i++){
        var publication = publications[i];
        if (!visible.includes(publication)){
            invisible.push(publication);
        }
    }

    for(var i = 0; i < visible.length; i++){
        visible[i].style.display = "block";
        
    }
    
    for(var i = 0; i < invisible.length; i++){
        invisible[i].style.display = "none";
        
    }

}

function lookForEmptySearch() {
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();

    if (filter === "") {

        var nav_elts = document.getElementsByClassName("navigation");

        for (var i = 0; i < nav_elts.length; i++) {
            nav_elts[i].style.display = "";
        }

        var pubs = document.getElementsByClassName("publication");

        for (var i = 0; i < pubs.length; i++) {
            pubs[i].style.display = "none";
        }
        showPublication(currentPage);
        updatePageNumber();
    }
}

// Event listener for the search input
document.getElementById('searchInput').addEventListener('input', filterPublications);

setInterval(lookForEmptySearch, 100);