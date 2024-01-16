import requests
from bs4 import BeautifulSoup
from parsel import Selector
import pandas as pd
import json
import re

def extract_user_id(url):
    pattern = r'user=([^&]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

def getAuthorProfileData(ScholarURL):
    try:
        # Existing code for BeautifulSoup
        url = ScholarURL
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        # print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Existing code to extract basic author information
        author_results = {}
        author_results['name'] = soup.select_one("#gsc_prf_in").get_text()
        author_results['position'] = soup.select_one("#gsc_prf_inw+ .gsc_prf_il").text
        author_results['email'] = soup.select_one("#gsc_prf_ivh").text
        author_results['published_content'] = soup.select_one("#gsc_prf_int").text

        # Printing basic author information
        print(f"Author Name: {author_results['name']}")
        print(f"Author Position: {author_results['position']}")
        # print(f"Author Email: {author_results['email']}")
        # print(f"Published Content: {author_results['published_content']}")

        # New code to extract articles using parsel
        userID = extract_user_id(ScholarURL)
        print("User ID is: " + userID)
        params = {
            'user': userID,
            'hl': 'en',
            'gl': 'us',
            'cstart': 0,
            'pagesize': '100'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        all_articles = []
        while True:
            html = requests.get('https://scholar.google.com/citations', params=params, headers=headers, timeout=30)
            selector = Selector(text=html.text)

            # getting 0 - 100 articles
            for index, article in enumerate(selector.css('.gsc_a_tr'), start=1):
                article_title = article.css('.gsc_a_at::text').get()
                article_link = f"https://scholar.google.com{article.css('.gsc_a_at::attr(href)').get()}"
                article_authors = article.css('.gsc_a_at+ .gs_gray::text').get()
                article_publication = article.css('.gs_gray+ .gs_gray::text').get()
                cited_by_count = article.css('.gsc_a_ac::text').get()
                publication_year = article.css('.gsc_a_hc::text').get()
                all_articles.append({
                    'position': index,
                    'title': article_title,
                    'link': article_link,
                    'authors': article_authors,
                    'publication': article_publication,
                    'publication_year': publication_year,
                    'cited_by_count': cited_by_count
                })

            if selector.css('.gsc_a_e').get():
                break
            else:
                params['cstart'] += 100

        # # # Printing information for each article
        # # print("Articles:")
        # for i, article in enumerate(all_articles, start=1):
        #     print(f"Article {i}:")
        #     for key, value in article.items():
        #         print(f"{key}: {value}")
        #     print()

        # New code to extract cited by information using parsel
        params_cited_by = {
            'user': userID,  # user-id
            'hl': 'en'  # language
        }
        headers_cited_by = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        html_cited_by = requests.get('https://scholar.google.com/citations', params=params_cited_by, headers=headers_cited_by, timeout=30)
        selector_cited_by = Selector(text=html_cited_by.text)
        data_cited_by = {
            'cited_by': [],
            'graph': []
        }
        since_year = selector_cited_by.css('.gsc_rsb_sth~ .gsc_rsb_sth+ .gsc_rsb_sth::text').get().lower().replace(' ', '_')
        for cited_by_public_access in selector_cited_by.css('.gsc_rsb'):
            data_cited_by['cited_by'].append({
                'citations_all': cited_by_public_access.css('tr:nth-child(1) .gsc_rsb_sc1+ .gsc_rsb_std::text').get(),
                f'citations_since_{since_year}': cited_by_public_access.css('tr:nth-child(1) .gsc_rsb_std+ .gsc_rsb_std::text').get(),
                'h_index_all': cited_by_public_access.css('tr:nth-child(2) .gsc_rsb_sc1+ .gsc_rsb_std::text').get(),
                f'h_index_since_{since_year}': cited_by_public_access.css('tr:nth-child(2) .gsc_rsb_std+ .gsc_rsb_std::text').get(),
                'i10_index_all': cited_by_public_access.css('tr~ tr+ tr .gsc_rsb_sc1+ .gsc_rsb_std::text').get(),
                f'i10_index_since_{since_year}': cited_by_public_access.css('tr~ tr+ tr .gsc_rsb_std+ .gsc_rsb_std::text').get(),
                #*********************************
                'articles_num': cited_by_public_access.css('.gsc_rsb_m_a:nth-child(1) span::text').get().split(' ')[0],
                'articles_link': f"https://scholar.google.com{cited_by_public_access.css('#gsc_lwp_mndt_lnk::attr(href)').get()}"
            })
        for graph_year, graph_yaer_value in zip(selector_cited_by.css('.gsc_g_t::text'), selector_cited_by.css('.gsc_g_al::text')):
            data_cited_by['graph'].append({
                'year': graph_year.get(),
                'value': int(graph_yaer_value.get())
            })
        # print(json.dumps(data_cited_by, indent=2, ensure_ascii=False))

        # New code to extract author information using parsel
        params_author_info = {
            'user': userID,  # user-id
            'hl': 'en'  # language
        }
        headers_author_info = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        html_author_info = requests.get('https://scholar.google.com/citations', params=params_author_info, headers=headers_author_info, timeout=30)
        selector_author_info = Selector(text=html_author_info.text)
        author_info = {}
        author_info['name'] = selector_author_info.css('#gsc_prf_in::text').get()
        author_info['affiliation'] = selector_author_info.css('#gsc_prf_inw+ .gsc_prf_il::text').get()
        author_info['email'] = selector_author_info.css('#gsc_prf_inw+ .gsc_prf_il::text').get()
        author_info['website'] = selector_author_info.css('.gsc_prf_ila::attr(href)').get()
        author_info['interests'] = selector_author_info.css('#gsc_prf_int .gs_ibl::text').getall(),
        author_info['thumbnail'] = selector_author_info.css('#gsc_prf_pup-img::attr(src)').get()
        # print(json.dumps(author_info, indent=2, ensure_ascii=False))

        # Convert data to DataFrames
        df_articles = pd.DataFrame(all_articles)
        df_cited_by = pd.DataFrame(data_cited_by['cited_by'])

        # Save data to CSV
        df_articles.to_csv(author_results['name']+'_Papers'+'.csv', index=False)
        df_cited_by.to_csv(author_results['name']+'_Profile'+'.csv', index=False)

    except Exception as e:
        print(e)

url_list = ['https://scholar.google.com/citations?user=PT8wxO8AAAAJ&hl=en','https://scholar.google.com/citations?user=T-CSbJgAAAAJ&hl=en&oi=hraa','https://scholar.google.com/citations?user=2LlnnZUAAAAJ&hl=en&oi=ao']

for list_item in url_list:
    print('Processing: ', list_item)
    getAuthorProfileData(list_item)
    print('Finished!'+'\n')




