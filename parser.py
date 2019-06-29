from html.parser import HTMLParser


class CVPRParser(HTMLParser):
    def __init__(self):
        super(CVPRParser, self).__init__()
        self.flag_intr = False
        self.flag_intd = False
        self.counter_td = 0
        self.cvpr_papers = []
        self.paper_ids = []

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.flag_intr = True
            self.counter_td = 0
            self.cvpr_paper = {}
        elif tag == 'td':
            self.flag_intd = True
            self.counter_td += 1

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.flag_intr = False
            # At least title should be provided
            if 'title' in self.cvpr_paper and 'id' in self.cvpr_paper:
                # Remove the duplicates
                if self.cvpr_paper['id'] not in self.paper_ids:
                    self.paper_ids.append(self.cvpr_paper['id'])
                    self.cvpr_papers.append(self.cvpr_paper)
        elif tag == 'td':
            self.flag_intd = False

    def handle_data(self, data):
        if self.flag_intr and self.flag_intd:
            if self.counter_td == 4:
                # Title of the paper
                self.cvpr_paper['title'] = data.strip()
            elif self.counter_td == 5:
                # Authors of the paper
                self.cvpr_paper['authors'] = [name.strip() for name in data.split(';')]
            elif self.counter_td == 6:
                # ID of the paper
                self.cvpr_paper['id'] = int(data)
            else:
                pass
