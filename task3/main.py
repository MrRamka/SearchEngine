import json
from ast import literal_eval
import os
import pymorphy2

from task2.main import lemmatize


# nltk.download('wordnet')
# nltk.download('omw-1.4')

class CountHelper:
    def __init__(self, lemma_path, document_dir):
        self.indexes = dict()
        self.word_mapping = dict()
        self.lemma_path = lemma_path
        self.document_dir = document_dir
        self.morph = pymorphy2.MorphAnalyzer()

    def write_mapping(self):
        file = open("index.json", "wb")
        file_data = json.dumps(self.indexes, ensure_ascii=False)
        file.write(file_data.encode('utf-8'))
        file.close()

    def read_lemmas_file(self):
        try:
            file_lines = self.get_file_lines(self.lemma_path)
            word_mapping = dict()
            for line in file_lines:
                key, value = line.split(" ", 1)
                # remove \n
                value = value[:len(value) - 1]
                # convert to list
                list_of_values = literal_eval(value)
                word_mapping[key] = list_of_values
            self.word_mapping = word_mapping
            print("The lemma file was read successfully")
        except IOError as e:
            print("Can`t read lemma file")
            print(e)

    def create_document_word_mapping(self):
        try:
            indexes = dict()
            for file in os.listdir(self.document_dir):
                print(f"Process file: {file}")
                file_path = self.document_dir + os.sep + file
                current_file_lines = self.get_file_lines(file_path)
                used_words = set()
                file_number_start_idx = file.index("_") + 1
                file_number_end_idx = len(file) - 4
                file_number = (file[file_number_start_idx: file_number_end_idx])
                for word in current_file_lines:
                    clean_word = word[:len(word) - 1]
                    normal_form = self.get_normal_form(clean_word)
                    lemma_word = lemmatize([normal_form])
                    lemma_word_key, _ = list(lemma_word.items())[0]
                    if lemma_word_key in self.word_mapping.keys() and normal_form not in used_words:
                        used_words.add(normal_form)
                        if lemma_word_key in indexes.keys():
                            indexes[lemma_word_key].append(file_number)
                        else:
                            indexes[lemma_word_key] = [file_number]
            self.indexes = indexes
        except IOError as e:
            print(f"Cant read file: {e}")

    @staticmethod
    def get_file_lines(file_name):
        try:
            file = open(file_name, "r", encoding="utf-8")
            file_lines = file.readlines()
            return file_lines
        except IOError:
            print(f"Cant read file {file_name}")

    def get_normal_form(self, word):
        p = self.morph.parse(word)[0]
        if p.normalized.is_known:
            normal_form = p.normal_form
        else:
            normal_form = word.lower()
        return normal_form

    def run(self):
        self.read_lemmas_file()
        self.create_document_word_mapping()
        self.write_mapping()
        print(f"Total words: {len(self.indexes.keys())}")


LEMMA_PATH = "../task2/lemmas.txt"
DOCUMENT_LEMMA_DIR = "../task2/data"
helper = CountHelper(LEMMA_PATH, DOCUMENT_LEMMA_DIR)

helper.run()
