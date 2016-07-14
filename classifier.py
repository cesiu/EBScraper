# Attempts to guess how an MOC should be classified.
# author: Christopher (cesiu)
# version: 0.1

from sys import argv
from re import sub
import string
import pickle
import os

# Represents one token and how often its used for each classification.
class Keyword:
    def __init__(self, token):
        self.token = token
        self.frequencies = {"OT": 0, "PT": 0, "CW": 0, "EU": 0, "ST": 0, "OR": 0}

# Contains the classification function so that the saved keywords are only
# loaded once and always saved when done.
class Classifier:
    def __enter__(self):
        # Load the saved keywords.
        self.keywords = {}
        if "keywords.p" in os.listdir(os.getcwd()):
            self.keywords = pickle.load(open("keywords.p", "rb"))

        # Ignore the conjunctions, pronouns, prepositions, 'be' verbs, and 
        # auxilliary verbs.
        self.common = dict([(word, True) for word in ["and", "but", "or", \
         "nor", "for", "yet", "so", "either", "not", "neither", "both", \
         "whether", "as", "rather", "a", "an", "the", "i", "he", "she" "me", \
         "him", "her", "they", "them", "we", "us", "my", "his", "her", \
         "hers", "their", "theirs", "our", "you", "your", "yours", "it", \
         "its", "aboard", "about", "above", "abreast", "abroad", "absent", \
         "across", "adjacent", "after", "against", "along", "alongside", \
         "amid", "among", "around", "as", "astride", "at", "atop", "before", \
         "behind", "below", "beneath", "beside", "besides", "between", \
         "beyond", "by", "circa", "come", "despite", "down", "during", \
         "except", "for", "from", "in", "inside", "into", "less", "like", \
         "minus", "near", "nearer", "nearest", "of", "off", "on", "onto", \
         "ontop", "opposite", "out", "outside", "over", "past", "per", \
         "post", "pre", "pro", "re", "sans", "save", "short", "since", \
         "than", "through", "thru", "throughout", "to", "toward", "towards", \
         "under", "underneath", "unlike", "until", "til", "till", "up", \
         "upon", "upside", "versus", "vs", "vs.", "via", "with", "within", \
         "without", "worth", "be", "being", "been", "am", "are", "is", "was", \
         "were", "can", "could", "dare", "do", "does", "did", "have", "has", \
         "had", "having", "may", "might", "must", "need", "ought", "shall", \
         "should", "will", "would"]])
        return self

    # Determines if a word is significant enough to be considered.
    # token - the word
    # returns True or False
    def is_significant(self, token):
        return len(token) > 1 and not token in self.common and not \
               token.isdigit() and not '\\x' in token and not \
               "http//www" in token 

    # Classifies a block of text.
    # text - the block to be classified
    # returns the classification, a string
    def check(self, text):
        # A text block is initially equally likely to be of any classification.
        guess = {"OT": 0, "PT": 0, "CW": 0, "EU": 0, "ST": 0, "OR": 0}

        # For each word in the block: 
        for token in text.split():
            token = sub("[().,:!'\";-]", '', token.lower())
            # Ignore short and common words.
            if self.is_significant(token):
                # If we've seen the word before, note how often it's used for
                # each classification.
                if token in self.keywords:
                    for classification, frequency \
                        in self.keywords[token].frequencies.iteritems():
                        guess[classification] += frequency
                # Else add a new object for it to the keyword dict. 
                else:
                    self.keywords[token] = Keyword(token)
        
        # Guess which classification most likely applies to the text block and
        # ask the user to confirm or correct.
        result = max(guess, key=guess.get)
        confirm = raw_input(result)
        if confirm != "y":
            result = raw_input("Correction: ")

        # Update the frequencies once we know the correct classification.
        for token in text.split():
            token = sub("[().,:!'\";-]", '', token.lower())
            if self.is_significant(token):
                self.keywords[token].frequencies[result] += 1
        return result

    def __exit__(self, exc_type, exc_value, traceback):
        pickle.dump(self.keywords, open("keywords.p", "wb"))

if __name__ == "__main__":
    with Classifier() as c:
        while True:
            print c.is_significant(raw_input("Enter text: "))