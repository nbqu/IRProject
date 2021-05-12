import re

class RawDocument:
    def __init__(self):
        self.docID = 0
        self.title = ''
        self.contents = ''

class ParsedDocument:
    def __init(self):
        pass

docs = []
with open('corpus.txt', 'r') as f:
    r = re.compile('<[^<>]*>')
    p = None
    for line in f.readlines():
        if line == '':
            continue
        if r.match(line):
            title = r.split(line)
            title = list(map(lambda x: x.strip(), title))
            title = list(filter(lambda x: x != '', title))
            title = title[0].split('.')
            p = RawDocument()


            p.docID = int(title[0])
            p.title = title[1].strip()

            docs.append(p)
            print(title)
        else:
            p.contents += line

for i in docs:
    print(f"title: {i.title}")
    print(f"contents: {i.contents}")

