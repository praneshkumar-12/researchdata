from django.shortcuts import render, redirect
from django.http import HttpResponse
from rpa.models import Publications
from rpa.models import Users
from rpa.forms import PublicationsForm
import rpa.extractor.extractor as Extractor
from django.http import JsonResponse

# Create your views here.

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        passcode = request.POST.get("pass")
        
        users = Users.objects.all()

        for user in users:
            if user.email_id == email and user.passkey == passcode:
                request.session["FACULTY_NAME"] = user.staff_name.split(" ")[0]
                return redirect('/rpa/auth/dashboard')

        # if email == "admin@ssn.edu.in" and passcode == "12345":
        else:
            return render(request, "index.html", context={"invalidlogin": True})
            
    return render(request, 'index.html')    

def dashboard(request):

    papers = Publications.objects.all()

    publication_list = []

    name = request.session["FACULTY_NAME"]

    form = PublicationsForm()

    for paper in papers:
        if name in paper.first_author or name in paper.second_author or name in paper.third_author or name in paper.other_authors:
            publication_list.append(paper)

    context = {'papers': publication_list, 'form': form, 'new_sno': f'{int(len(publication_list)) + 1}'}

    # paper_records = 
    return render(request, 'layout.html', context)



def verify_paper(request):
    uniqueid = request.POST.get("uniqueid")

    current_paper = Publications.objects.get(uniqueid=uniqueid)
    current_paper.verified = "True"
    current_paper.save()

    return HttpResponse(f"Updated verification status for {current_paper.title}")

def scrape_data(request):
    # title = request.POST.get("title", "")
    doi = request.POST.get("doi", "")

    title = Extractor.get_title(doi)

    search_query = title + doi
    try:
        result = Extractor.main(search_query)
    except (IndexError, KeyError):
        return HttpResponse("Cannot fetch data for the given search term!")

    print(result)

    if (result is None) or (result == False):
        return HttpResponse("Cannot fetch data for the given search term!")
    else:
        return JsonResponse(result)
