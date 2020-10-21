import os
import re
import requests
import urllib

from tqdm import tqdm
from unidecode import unidecode


class Crawler(object):
    def __init__(self, keyword, timeout=5.0, download_arxiv=True, download_openaccess=True, verbose=False, use_tqdm=True):
        self.arxiv_query_url = "https://arxiv.org/search/?query={}&searchtype=all&source=header"
        self.openaccess_html_query_url = "http://openaccess.thecvf.com/content_CVPR_2019/html/{}_CVPR_2019_paper.html"
        self.openaccess_pdf_query_url = "http://openaccess.thecvf.com/content_CVPR_2019/papers/{}_CVPR_2019_paper.pdf"

        self.keyword = keyword
        self.timeout = timeout
        self.download_arxiv = download_arxiv
        self.download_openaccess = download_openaccess

        self.verbose = verbose
        self.use_tqdm = use_tqdm
        if use_tqdm:
            self.print_function = tqdm.write
        else:
            self.print_function = print

    def client(self, paper):
        # arXiv
        title_url = urllib.parse.quote(paper["title"])
        query = self.arxiv_query_url.format(title_url)
        r = requests.get(query, timeout=self.timeout)
        if r.ok:
            # Successful connection
            arxiv_links = [
                link.split('"')[1]
                for link in r.text.split()
                if "https://arxiv.org/abs/" in link
            ]
            paper["arxiv"] = arxiv_links

            # arXiv pdf
            if self.download_arxiv:
                arxiv_pdf_links = [
                    link.replace("abs", "pdf") + ".pdf"
                    for link in arxiv_links
                ]
                for query in arxiv_pdf_links:
                    r = requests.get(query, stream=True, timeout=self.timeout)
                    if r.ok:
                        # Successful connection
                        filename = os.path.join(
                            "results",
                            self.keyword,
                            "arxiv",
                            query.split("/")[-1]
                        )
                        with open(filename, "wb") as f:
                            f.write(r.content)
                    else:
                        self._print_failure(paper["title"], "arxiv pdf server", r.status_code)
        else:
            self._print_failure(paper["title"], "arxiv html server", r.status_code)

        # Open Access
        auth1_ = paper["authors"][0].split()[-1]
        title_ = paper["title"].replace(" ", "_")
        query_ = auth1_ + "_" + title_
        query_ = unidecode(query_)
        query_ = re.sub("[^\w_-]", "", query_)
        query = self.openaccess_html_query_url.format(query_)
        r = requests.head(query, timeout=self.timeout)
        if r.ok:
            # Successful connection
            paper["openaccess"] = query

            # Open Access pdf
            if self.download_openaccess:
                query = self.openaccess_pdf_query_url.format(auth1_, title_)
                r = requests.get(query, stream=True, timeout=self.timeout)
                if r.ok:
                    # Successful connection
                    filename = os.path.join(
                        "results",
                        self.keyword,
                        "openaccess",
                        "{}_{}.pdf".format(auth1_, title_)
                    )
                    with open(filename, "wb") as f:
                        f.write(r.content)
                else:
                    self._print_failure(paper["title"], "openaccess pdf server", r.status_code)
        else:
            self._print_failure(paper["title"], "openaccess html server", r.status_code)

    def _print_failure(self, title, root, status_code):
        self.print_function("{} failed on request to {}: {:d}" \
            .format(title, url, status_code))


