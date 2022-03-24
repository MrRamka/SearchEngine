import json
import math
import os
from pathlib import Path

import pymorphy2
from nltk import WordNetLemmatizer


class TFIDFHelper:
    def __init__(self, index_file, page_count, tokens_dir):
        self.indexes = dict()
        self.word_mapping = dict()
        self.page_count = page_count
        self.index_file = index_file
        self.tokens_dir = tokens_dir
        self.morph = pymorphy2.MorphAnalyzer()
        self.lemmatizer = WordNetLemmatizer()

    def create_tf(self):
        pass

    def run(self):
        print("Create folders")
        Path("data/token").mkdir(parents=True, exist_ok=True)
        Path("data/lemma").mkdir(parents=True, exist_ok=True)
        print("Read indexes file")
        self.read_indexes_file(self.index_file)
        print(f"Process tokens file")
        token_idf = self.get_idf()
        print(f"Process lemmas file")
        lemmas_idf = self.get_idf(True)
        for file in os.listdir(self.tokens_dir):
            print(f"Process: {file}")
            file_path = self.tokens_dir + file
            idx = file.split("_")[1].split(".")[0]
            tokens_tf_file = self.get_idf_file(file_path)
            self.write_result_to_file(f"./data/token/token_{idx}.txt", tokens_tf_file, token_idf)

            lemmas_tf_file = self.get_idf_file(file_path)
            self.write_result_to_file(f"./data/lemma/lemma_{idx}.txt", lemmas_tf_file, lemmas_idf)

    def read_indexes_file(self, path):
        try:
            file = open(path, "r", encoding="utf-8")
            lines = file.readlines()
            self.indexes = json.loads(lines[0])
        except Exception:
            print("Cant read indexes file")

    @staticmethod
    def read_tokens(file_tokens_path):
        with open(file_tokens_path, 'r', encoding="utf-8") as file:
            file_tokens = list(map(lambda word: word[:-1], file.readlines()))
        return file_tokens

    def get_idf(self, lemmatize=False):
        print("Start idf")
        idfs = dict()
        for token, documents in self.indexes.items():
            df = len(documents)
            idf = math.log(self.page_count / df)
            if lemmatize:
                token = self.lemma_function(token)
            idfs[token] = idf
        return idfs

    def lemma_function(self, token):
        p = self.morph.parse(token)[0]
        if p.normalized.is_known:
            token = p.normal_form
        else:
            lemmatized = self.lemmatizer.lemmatize(token)
            token = lemmatized.lower()
        return token

    def get_idf_file(self, file_path, lemmatize=False):
        file_tokens = self.read_tokens(file_path)
        tf = dict()
        if lemmatize:
            func = lambda tk: self.lemma_function(tk)
            file_tokens = list(map(func, file_tokens))
        for token in file_tokens:
            tf[token] = file_tokens.count(token) / len(file_tokens)
        return tf

    def write_result_to_file(self, path, tfs, idfs):
        with open(path, mode='w', encoding='utf-8') as file:
            for token, tf in tfs.items():
                idf = idfs.get(token)
                if idf:
                    tf_idf = tf * idf
                    file.write(f'{token}: {idf} {tf_idf}\n')


indexes = "../task3/index.json"
lemmas = "../task2/lemmas.txt"
tokens = "../task2/data/"
amount = 150
helper = TFIDFHelper(indexes, amount, tokens)
helper.run()
