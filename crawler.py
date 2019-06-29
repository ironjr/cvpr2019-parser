import os
import requests
import urllib


class Crawler(object):
    def __init__(self, keyword, timeout=1.0):
        self.arxiv_query_url = 'https://arxiv.org/search/?query={}&searchtype=all&source=header'
        self.openaccess_html_query_url = 'http://openaccess.thecvf.com/content_CVPR_2019/html/{}_{}_CVPR_2019_paper.html'
        self.openaccess_pdf_query_url = 'http://openaccess.thecvf.com/content_CVPR_2019/papers/{}_{}_CVPR_2019_paper.pdf'

        self.keyword = keyword
        self.timeout = timeout

    def client(self, paper):
        # arXiv
        title_url = urllib.parse.quote(paper['title'])
        query = self.arxiv_query_url.format(title_url)
        r = requests.get(query, timeout=self.timeout)
        if r.status_code == 200:
            # Successful connection
            arxiv_links = [link.split('"')[1] for link in r.text.split() if 'https://arxiv.org/abs/' in link]
            paper['arxiv'] = arxiv_links

        # Open Access
        auth1_ = paper['authors'][0].split()[-1]
        title_ = paper['title'].replace(':', '').replace(' ', '_')
        query = self.openaccess_html_query_url.format(auth1_, title_)
        r = requests.head(query, timeout=self.timeout)
        if r.status_code == 200:
            # Successful connection
            paper['openaccess'] = query

        # Open Access pdf
        query = self.openaccess_pdf_query_url.format(auth1_, title_)
        r = requests.get(query, stream=True, timeout=self.timeout)
        if r.status_code == 200:
            # Successful connection
            with open(os.path.join(self.keyword, '{}_{}.pdf'.format(auth1_, title_)), 'wb') as f:
                f.write(r.content)


