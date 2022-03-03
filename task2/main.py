import re

import nltk
from bs4 import BeautifulSoup
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import os
from pathlib import Path

NLTK_PACKAGES = [
    'tokenizers/punkt', 'corpora/stopwords', 'corpora/wordnet', 'corpora/omw-1.4']
for package in NLTK_PACKAGES:
    try:
        nltk.find(package)
    except Exception:
        nltk.download(package.split('/')[1])

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


def cleanhtml(text):
    clean_reg_ex = re.compile('<.*?>')
    clean_text = re.sub(clean_reg_ex, '', text)
    return clean_text


def remove_chars(text):
    clean_text = re.sub('\s+', ' ', text)
    return clean_text


def stop_words(tokenize_words):
    stopWords = set(stopwords.words('english'))
    wordsFiltered = []
    for w in tokenize_words:
        if w not in stopWords:
            wordsFiltered.append(w)
    return wordsFiltered


def write_file(filename, words):
    file = open("data\\" + filename, 'w', encoding='utf-8')
    for word in words:
        file.write(f'{word}\n')


def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    lemma_token = dict()

    for token in tokens:

        lemmatized = lemmatizer.lemmatize(token)

        mapped_tokens = lemma_token.get(lemmatized, [])
        mapped_tokens.append(token)

        lemma_token[lemmatized] = mapped_tokens
    return lemma_token


def normalize_data():
    data_path = os.path.join(os.path.dirname(CURRENT_PATH), 'task1', 'task1', 'pages')
    Path("data").mkdir(parents=True, exist_ok=True)
    all_tokens = []
    for file_name in os.listdir(data_path):
        print(f"Normalize: {file_name}")
        with open(os.path.join(data_path, file_name), 'r', encoding='utf-8') as data_file:
            raw_data_file = data_file.read()

            soup = BeautifulSoup(raw_data_file, features="html.parser")
            cleaned_html_data = soup.get_text()

            cleaned_chars = remove_chars(cleaned_html_data)

            # remove punctuation
            tokenizer = RegexpTokenizer(r'\w+')
            tokenizer_text = tokenizer.tokenize(cleaned_chars)

            # lower case
            tokens = [w.lower() for w in tokenizer_text]

            # remove stop words
            filtered_tokens = stop_words(tokens)

            # Remove numbers
            filtered_tokens = [word for word in filtered_tokens if word.isalpha()]

            write_file(file_name.replace(".html", ".txt"), filtered_tokens)

            all_tokens += filtered_tokens

    lemmatize_tokens = lemmatize(list(set(all_tokens)))
    with open("lemmas.txt", 'w', encoding='utf-8') as lemmas:
        for key, value in lemmatize_tokens.items():
            lemmas.write(f'{key}: {value}\n')


if __name__ == '__main__':
    # nltk.download('punkt')
    # nltk.download('stopwords')
    normalize_data()
