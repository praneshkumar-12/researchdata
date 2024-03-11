const buttons = document.querySelectorAll('.btn-custom');

function removeActiveClass() {
    buttons.forEach(button => {
        button.classList.remove('active');
    });
}

// Function to handle button click
function handleUnverified(event) {
    // Remove active class from all buttons
    removeActiveClass();

    // Add active class to the clicked button
    event.target.classList.add('active');

    var papers = document.getElementsByClassName('publication');

    for (var i = 0; i < papers.length; i++){
        var paper = papers[i];


        var span_elt = paper.getElementsByTagName('span')[0];

        if (span_elt.id == "unverified"){
            paper.style.display = 'block';
        }
        else{
            paper.style.display = 'none';
        }
        
    }
}

function handleUnderVerification(event) {
    // Remove active class from all buttons
    removeActiveClass();

    // Add active class to the clicked button
    event.target.classList.add('active');

    var papers = document.getElementsByClassName('publication');

    for (var i = 0; i < papers.length; i++){
        var paper = papers[i];


        var span_elt = paper.getElementsByTagName('span')[0];

        if (span_elt.id == "underVerification"){
            paper.style.display = 'block';
        }
        else{
            paper.style.display = 'none';
        }
        
    }
}

function handleVerified(event) {
    // Remove active class from all buttons
    removeActiveClass();

    // Add active class to the clicked button
    event.target.classList.add('active');

    var papers = document.getElementsByClassName('publication');

    for (var i = 0; i < papers.length; i++){
        var paper = papers[i];


        var span_elt = paper.getElementsByTagName('span')[0];

        if (span_elt.id == "verified"){
            paper.style.display = 'block';
        }
        else{
            paper.style.display = 'none';
        }
        
    }
}

function filterPublications() {

    var input, filter, publications, publication, title, i, txtValue;
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();
    if (filter === "") return filter
    publications = document.getElementsByClassName('publication');
    var searchTerms = filter.split(" ").filter(term => term.trim() !== "");

    console.log(searchTerms);

    var visible = [];
    var invisible = [];

    for(var i = 0; i < publications.length; i++){
        var publication = publications[i];
        title = publication.getElementsByTagName("a")[0].innerHTML.toUpperCase();
        var found = true;        
        for (var k = 0; k < searchTerms.length; k++) {
            if (title.includes(searchTerms[k].toUpperCase()) && publication.getAttribute('data-isvisible') === "yes"){
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

        var pubs = document.getElementsByClassName("publication");

        for (var i = 0; i < pubs.length; i++) {
            if (pubs[i].getAttribute('data-isvisible') === 'yes'){
                pubs[i].style.display = 'block';
            }
        }
    }
}


// Add click event listener to all buttons
document.getElementById('unverifiedBtn').addEventListener('click', handleUnverified);
document.getElementById('underVerificationBtn').addEventListener('click', handleUnderVerification);
document.getElementById('verifiedBtn').addEventListener('click', handleVerified);

document.getElementById('searchInput').addEventListener('input', filterPublications);
setInterval(lookForEmptySearch, 100);

document.addEventListener("DOMContentLoaded", function() {
    var papers = document.getElementsByClassName('publication');

    for (var i = 0; i < papers.length; i++){
        var paper = papers[i];


        var span_elt = paper.getElementsByTagName('span')[0];

        if (span_elt.id == "unverified"){
            paper.style.display = 'block';
        }
        
    }
});