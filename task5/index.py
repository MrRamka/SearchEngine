import json
import re

from nltk import word_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from scipy.spatial import distance

# nltk.download('punkt')
# nltk.download('stopwords')
pattern = re.compile("^[a-zA-Z]+$")
STOPWORDS = stopwords.words('english')


class SearchHelper:
    def __init__(self, indexes_path, files_path, response_limit = 10):
        self.files = []
        self.matrix = [[]]
        self.indexes = []
        self.read_indexes_file(indexes_path)

        self.pymorphy2_analyzer = MorphAnalyzer()
        self.read_websites(files_path)
        self.response_limit = response_limit

    def read_indexes_file(self, path):
        try:
            file = open(path, "r", encoding="utf-8")
            lines = file.readlines()
            all_indexes = dict(json.loads(lines[0]))
            self.indexes = list(all_indexes.keys())
            self.matrix = [[0] * 150 for _ in range(len(self.indexes))]
            for idx, item in enumerate(all_indexes):
                values = all_indexes.get(item)
                for value in values:
                    self.matrix[idx][int(value) - 1] = 1
        except Exception:
            print("Cant read indexes file")

    @staticmethod
    def get_column(matrix, i):
        return [row[i] for row in matrix]

    def get_vector(self, search_string):
        search_string = " ".join(search_string.split("+"))
        search_tokens = word_tokenize(search_string)
        print(search_tokens)
        lowered_tokens = [line_token.lower() for line_token in search_tokens]
        cleaned_search_tokens = [item for item in lowered_tokens if item not in STOPWORDS and pattern.match(item)]

        tokens_normal_form = [self.pymorphy2_analyzer.parse(token)[0].normal_form for token in cleaned_search_tokens]
        vector = [0] * (len(self.indexes))
        for token in tokens_normal_form:
            if token in self.indexes:
                vector[self.indexes.index(token)] = 1
        return vector

    def search(self, query):
        print(query)
        vector = self.get_vector(query)
        docs = dict()
        for idx in range(len(self.matrix[0])):
            current_vector = self.get_column(self.matrix, idx)
            if max(current_vector) == 1:
                docs[idx + 1] = 1 - distance.cosine(vector, current_vector)
            else:
                docs[idx + 1] = 0.0

        sorted_docs = sorted(docs.items(), key=lambda x: x[1], reverse=True)
        indexed_docs = [(list(filter(lambda source: source["file_name"] == f"source_{doc[0]}.html", self.files)), doc)
                        for doc in sorted_docs]
        return indexed_docs[:self.response_limit]

    def read_websites(self, path):
        try:
            with open(path, 'r', encoding="utf-8") as outfile:
                self.files = json.load(outfile)
        except IOError:
            print("Cant read indexes file")


# indexes = "../task3/index.json"
# files_path = "../task1/task1/index.json"
# helper = SearchHelper(indexes, files_path)
# result = helper.search("Power BI")
# print(result)
