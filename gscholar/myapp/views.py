from django.shortcuts import render, redirect
from myapp.scraper.main import scraper


# author_urls = ['https://scholar.google.com/citations?user=PT8wxO8AAAAJ&hl=en',
#                'https://scholar.google.com/citations?user=T-CSbJgAAAAJ&hl=en&oi=hraa',
#                'https://scholar.google.com/citations?user=2LlnnZUAAAAJ&hl=en&oi=ao']


def home(request):
    response = redirect('/articles')
    return response


def articles(request):
    urls_query = request.GET.get('urls', '')
    search_query = request.GET.get('search', '')

    if urls_query.strip() == '':
        return render(request, "articles.html", {"articles": []})

    raw_urls = urls_query.split(',')
    urls = [url.strip() for url in raw_urls]

    data = scraper(urls, search_query) if len(urls) > 0 else []
    print(data)
    return render(request, "articles.html", {"urls": urls_query, "search": search_query, "articles": data})
