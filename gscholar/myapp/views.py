from django.shortcuts import render
from myapp.scraper.main import scraper


# author_urls = ['https://scholar.google.com/citations?user=PT8wxO8AAAAJ&hl=en',
#                'https://scholar.google.com/citations?user=T-CSbJgAAAAJ&hl=en&oi=hraa',
#                'https://scholar.google.com/citations?user=2LlnnZUAAAAJ&hl=en&oi=ao']


def home(request):
    return render(request, "home.html")


def articles(request):
    query = request.GET.get('urls', '')

    if query.strip() == '':
        return render(request, "articles.html", {"articles": []})

    raw_urls = query.split(',')
    urls = [url.strip() for url in raw_urls]

    data = scraper(urls) if len(urls) > 0 else []
    print(data)
    return render(request, "articles.html", {"query": query, "articles": data})
