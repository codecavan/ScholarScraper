from django.shortcuts import render
from myapp.scraper.main import getAuthorProfileData


def home(request):
    data = getAuthorProfileData()
    print(data)
    return render(request, "articles.html", {"articles": data})
