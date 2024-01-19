import requests
from bs4 import BeautifulSoup
from parsel import Selector
import pandas as pd
import re

gscholar_url = "https://scholar.google.com"
gscholar_citations_url = f"{gscholar_url}/citations"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
headers = {"User-Agent": user_agent}


def process_author_profile(url):
    try:
        # New code to extract articles using parsel
        user_id = extract_user_id(url)
        print("User ID is: " + user_id)

        articles = get_articles(user_id)
        return articles

    except Exception as e:
        print(e)


def extract_user_id(url):
    pattern = r'user=([^&]+)'
    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


def get_author_profile_data(url):
    response = requests.get(url, headers=headers)
    # print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Existing code to extract basic author information
    profile_data = {}
    profile_data['name'] = soup.select_one("#gsc_prf_in").get_text()
    profile_data['position'] = soup.select_one(
        "#gsc_prf_inw+ .gsc_prf_il").text
    profile_data['email'] = soup.select_one("#gsc_prf_ivh").text
    profile_data['published_content'] = soup.select_one(
        "#gsc_prf_int").text

    # Printing basic author information
    print(f"Author Name: {profile_data['name']}")
    print(f"Author Position: {profile_data['position']}")
    # print(f"Author Email: {author_results['email']}")
    # print(f"Published Content: {author_results['published_content']}")

    return profile_data


def get_articles(user_id):
    params = {
        'user': user_id,
        'hl': 'en',
        'gl': 'us',
        'cstart': 0,
        'pagesize': '100'
    }

    articles = []

    while True:
        html = requests.get(gscholar_citations_url,
                            params=params, headers=headers, timeout=30)
        selector = Selector(text=html.text)

        # getting 0 - 100 articles
        for index, article in enumerate(selector.css('.gsc_a_tr'), start=1):
            article_title = article.css('.gsc_a_at::text').get()
            article_link = f'''{gscholar_url}{
                article.css('.gsc_a_at::attr(href)').get()}'''
            article_authors = article.css(
                '.gsc_a_at+ .gs_gray::text').get()
            article_publication = article.css(
                '.gs_gray+ .gs_gray::text').get()
            cited_by_count = article.css('.gsc_a_ac::text').get()
            publication_year = article.css('.gsc_a_hc::text').get()

            articles.append({
                'user_id': user_id,
                'position': index + params['cstart'],
                'title': article_title,
                'link': article_link,
                'authors': article_authors,
                'publication': article_publication,
                'publication_year': publication_year,
                'cited_by_count': cited_by_count
            })

        if selector.css('.gsc_a_e').get():
            if len(articles) > 1 and articles[-1]['position'] == params['cstart'] + 1:
                articles.pop()

            break

        params['cstart'] += 100

    return articles


# url_list = ['https://scholar.google.com/citations?user=PT8wxO8AAAAJ&hl=en',
#             'https://scholar.google.com/citations?user=T-CSbJgAAAAJ&hl=en&oi=hraa', 'https://scholar.google.com/citations?user=2LlnnZUAAAAJ&hl=en&oi=ao']

def main(urls):
    merged_articles = []

    for url in urls:
        print('Processing: ', url)
        author_articles = process_author_profile(url)
        merged_articles += author_articles
        print('Finished!'+'\n')

    df_articles = pd.DataFrame(merged_articles)
    df_articles.to_csv('articles.csv', index=False)


if __name__ == "__main__":
    main()
