import re
from PyKomoran import *
import json
import numpy as np
import heapq

class RawDocument:
    def __init__(self):
        self.docID = 0
        self.title = ''
        self.contents = ''


class ParsedDocument:
    def __init__(self):
        self.docID = 0
        self.title = ''
        self.index = []
        self.tf_idf = None

    def __str__(self):
        return f'{self.docID}, {self.title}, {self.index}\n'

    __repr__ = __str__


"""
    positional index을 딕셔너리 크기에 맞게 tf로 변환
"""


def term_freq(indices, term_n):
    ret = np.array([0 for i in range(term_n+1)])
    for i in indices:
        ret[i] = 1
    return ret


def doc_freq(doc_n=100):
    with open('word_index.json', 'r') as d:
        content = json.load(d)
        term_n = len(content)
        ret = np.array([0 for i in range(term_n+1)])
        for i in range(1, term_n+1):
            ret[i] = np.log(doc_n/next(len(value['doc_id']) for key, value in content.items() if i == value['index']))

        return ret


def num_of_terms():
    with open('word_index.json', 'r') as d:
        return len(json.load(d))


docs = []
parsed_docs = []
komoran = Komoran(DEFAULT_MODEL['LIGHT'])
word_to_index = {}
"""
word: {
    'index': (word index),
    'doc_id': (standard inverted index, len == document frequency)
    'freq': (collection frequency)
    }
"""


def tokenize(string):
    return komoran.get_morphes_by_tags(string, tag_list=['NNG', 'NNP', 'VV', 'VA', 'VX',
                                                                       'MAG', 'XPN', 'XSN', 'XSV', 'XSA', 'XR', 'SL',
                                                                       'SN', 'SH', 'SW', 'NF', 'NV', 'NA'])


def make_vector(tokens):
    with open('word_index.json', 'r') as d:
        content = json.load(d)
        ret = np.array([0 for i in range(len(tokens))])
        for i in range(len(tokens)):
            if tokens[i] in content:
                ret[i] = content[tokens[i]]['index']
        return ret


def normalize(vec):
    norm = np.linalg.norm(vec)
    if norm:
        return vec/np.linalg.norm(vec)
    return vec
"""
    Corpus를 읽어와서 tokenize 한 뒤, word dictionary(word_index.json)과 parsed document corpus(parsed_doc.json)을 생성한다.
    Document의 제목은 user dictionary에 등록되어서 tokenizing 할 때 정확성을 높였다.
    flask가 실행될 때(서버가 실행될 때) 한 번 만 실행된다.
"""
def init():
    komoran.set_user_dic('./user_dic.txt')
    with open('corpus.txt', 'r') as f, open('user_dic.txt', 'w') as d, open('raw_doc.json', 'w', encoding='utf8') as rd :
        r = re.compile(r'<[^<>]*>')
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
                for s in p.title.split():
                    d.write(s + '\tNNG\n')


                docs.append(p)
                # print(title)
            else:
                p.contents += line.strip()

        json.dump([{'id': i.docID, 'title': i.title, 'contents': i.contents} for i in docs], rd, ensure_ascii=False, indent=4)

    for i in docs:
        p = ParsedDocument()
        p.title = i.title
        p.docID = i.docID
        parsed_docs.append(p)
        # print(f"title: {i.title}")
        # print(f"contents: {i.contents}")
        pos_tagged = tokenize(i.contents)
        for word in pos_tagged:
            if word not in word_to_index:
                word_to_index[word] = {'index': len(word_to_index)+1, 'doc_id': [i.docID], 'freq': 1}
            else:
                word_to_index[word]['freq'] += 1
                if word_to_index[word]['doc_id'][-1] < i.docID:
                    word_to_index[word]['doc_id'].append(i.docID)
        p.index = pos_tagged
        # print(pos_tagged)

    with open('word_index.json', 'w', encoding='utf8') as windex:
        json.dump(word_to_index, windex, ensure_ascii=False, indent=4)

    with open('parsed_doc.json', 'w', encoding='utf8') as pdoc, open('tf_idf.json', 'w', encoding='utf8') as vec:
        df = doc_freq()
        for i in parsed_docs:

            for j in range(len(i.index)):
                i.index[j] = word_to_index[i.index[j]]['index']
            i.tf_idf = term_freq(i.index, num_of_terms()) * df
        json.dump([{'id': i.docID, 'title': i.title, 'index': i.index} for i in parsed_docs], pdoc,
                  ensure_ascii=False, indent=4)
        json.dump([{'id': i.docID, 'tf_idf': normalize(i.tf_idf).tolist()} for i in parsed_docs], vec,
                  ensure_ascii=False, indent=4)

    print('initializing completed.')


def process_query(query):
    tokenized = tokenize(query)
    if tokenized:
        query_vec = make_vector(tokenized)
    else:
        query_vec = make_vector(query.split())
    query_tf = term_freq(query_vec, num_of_terms())
    return normalize(query_tf*doc_freq())


def consine_rank(query_tf_idf, top=5):
    heap = []
    with open('tf_idf.json', 'r') as pdoc, open('raw_doc.json', 'r') as rd:
        raw = json.load(rd)
        content = json.load(pdoc)
        for doc in content:
            heapq.heappush(heap, (-np.dot(np.array(doc['tf_idf']), query_tf_idf), doc['id']))

        ret = []
        for i in range(top):
            r = heapq.heappop(heap)
            if abs(r[0]) <= 10**-5:
                break
            res = raw[r[1]-1]
            ret.append((res['id'], res['title'], res['contents']))
            heapq.heapify(heap)
    return ret


