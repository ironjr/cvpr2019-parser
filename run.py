import argparse
import os
import multiprocessing as mp

from tqdm import tqdm

from crawler import Crawler
from parser import CVPRParser


def main(args):
    # TODO Perhaps add support for multiple keywords?
    keywords = [args.keyword,]

    with open('cvpr2019.txt', 'r') as f:
        # Parse the papers in the CVPR website
        parser = CVPRParser()
        while True:
            line = f.readline()
            if not line:
                break
            parser.feed(line)

        papers = parser.cvpr_papers
        print('Total {} # of papers detected'.format(len(papers)))

        # Search for the keywords
        print('')
        for keyword in keywords:
            result = [paper for paper in papers if keyword.lower() in paper['title'].lower()]
            print('CVPR papers with keyword: {}'.format(keyword))
            print('Total {} # of papers found'.format(len(result)))

            if not os.path.isdir(keyword):
                os.mkdir(keyword)

            # Search website for more information
            print('Download papers from online ...')
            crawler = Crawler(keyword)
            pbar = tqdm(total=len(result))
            def update_pbar(*args):
                pbar.update()

            pool = mp.Pool(mp.cpu_count())
            for i in range(len(result)):
                pool.apply_async(crawler.client, args=(result[i],), callback=update_pbar)
            pool.close()
            pool.join()
            print('')
            print('Download is now complete')
            print('')

            # Create line format to print pretty
            len_id = 0; len_title = 0
            for paper in result:
                len_id_new = len(str(paper['id']))
                if len_id < len_id_new:
                    len_id = len_id_new
                len_title_new = len(paper['title'])
                if len_title < len_title_new:
                    len_title = len_title_new
            line_format = '{:' + str(len_id + 2) + 's}' + \
                    '  ' + \
                    '{:' + str(len_title) + 's}' + \
                    '  ' + \
                    '{:s}'

            # Print the results
            print(line_format.format('ID', 'TITLE', '1st AUTHOR'))
            for paper in result:
                print(line_format.format(str(paper['id']), paper['title'], paper['authors'][0]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Paper search with downloader')
    parser.add_argument('--keyword', type=str, default='detection',
            help='search keywords in the paper title')
    args = parser.parse_args()

    main(args)
