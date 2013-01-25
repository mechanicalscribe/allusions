#!/usr/bin/env python
import os
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from collections import defaultdict
import math
from utils import mkdir_p
import argparse

#NLTK objects
punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs'])
sent_tokenize = PunktSentenceTokenizer(punkt_param)
stops = stopwords.words('english')

def lemmatize(text):
    return re.findall(r"\b[A-z-]+\b", text)

def get_bigrams(tokens, blur=1):
    grams = []
    if type(tokens) is str:
        tokens = lemmatize(tokens)
    elif type(tokens) is not list:
        print "Input must be string or list of tokens"
        return
    for c in range(len(tokens) - 1):
        for i in range(c + 1, min(c + blur + 1, len(tokens))):
            grams.append((tokens[c], tokens[i]))
    return grams

#get the word and bigram frequencies for every file in directory
def analyze(path, blur=1, remove_stops=True, cache=True):
    if path[-1] != "/":
        path += "/"

    freq = defaultdict(int)    
    all = {}

    #load every file in the directory
    for filenm in [f for f in os.listdir(path) if os.path.isfile(path + f)]:
        print filenm
        sentences = sent_tokenize.tokenize(open(path + filenm, 'r').read().replace("\n", " "))
        data = { 'words': [], 'bigrams': [], 'sentences': sentences }
        bigrams = []
        for sentence in sentences:
            if remove_stops:
                words = [word for word in lemmatize(sentence.lower()) if not word in stops]
            else:
                words = [word for word in lemmatize(sentence.lower())]                
            for word in words:
                freq[word] += 1
            
            bigrams = get_bigrams(words, blur)
            for bigram in bigrams:
                freq["_".join(bigram)] += 1
                
            data['words'].append(words)
            data['bigrams'].append(bigrams)
        
        if cache:
            mkdir_p(path + "parsed")
            f = open(path + "parsed/" + re.sub("\.[A-z]{1,4}$", "", filenm) + ".json", 'w')
            f.write(json.dumps(data, sort_keys=True))
            f.close()
        
        all[filenm] = data

    mkdir_p(path + "parsed")
    f = open(path + "parsed/all.json", 'w')
    f.write(json.dumps(all, sort_keys=True))
    f.close()


    #remove all entries with a frequency of one, since they're not repeated by definition
    freq = dict((k, v) for k, v in freq.iteritems() if v > 1 )              

    mkdir_p(path + "stats")
    f = open(path + "stats/frequencies.json", 'w')
    f.write(json.dumps(freq, sort_keys=True))
    f.close()    
    
def main():
    parser = argparse.ArgumentParser(description="Analyze word and bigram frequency in a directory of text files")
    parser.add_argument("-p", "--path", metavar="STRING", dest="path", type=str, default=None,
                        help="path of the files to scan")
    args = parser.parse_args()

    path = args.path

    if path is None:
        parser.error("You need to enter a path to the text files.")
    if path[0] == "/":
        path = os.getcwd() + path

    analyze(path)

if __name__ == "__main__":
    main()