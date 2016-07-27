# Attempts to guess how an MOC should be classified.
# author: Christopher (cesiu)
# version: 0.2

from sys import argv, stderr
from re import sub
import string
import pickle
import os

CLASSES = ["OTveh", "OTloc", "OTchr", "OTmin", \
           "PTveh", "PTloc", "PTchr", "PTmin", \
           "STveh", "STloc", "STchr", "STmin", \
           "CWveh", "CWloc", "CWchr", "CWmin", \
           "EUveh", "EUloc", "EUchr", "EUmin", \
           "NCveh", "NCloc", "NCchr", "NCmin", \
           "SPall"]

ERAS = ["OT", "PT", "ST", "EU", "CW", "NC", "SP"]
TYPES = ["veh", "loc", "chr", "min", "all"]

# Represents one token and how often its used for each classification.
class Keyword:
    def __init__(self, token):
        self.token = token
        self.era_freqs = dict([(key, 0) for key in ERAS])
        self.type_freqs = dict([(key, 0) for key in TYPES])

# Contains the classification function so that the saved keywords are only
# loaded once and always saved when done.
class Classifier:
    def __init__(self, auto=False):
        self.auto = auto

    def __enter__(self):
        # Load the saved keywords.
        self.keywords = {}
        if "keywords.p" in os.listdir(os.getcwd()):
            self.keywords = pickle.load(open("keywords.p", "rb"))

        # Load the saved ignored words.
        self.blacklist = {}
        if "ignorewords.p" in os.listdir(os.getcwd()):
            self.blacklist = pickle.load(open("ignorewords.p", "rb"))

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
        self.common.update(self.blacklist)

        return self

    # Determines if a word is significant enough to be considered.
    # token - the word
    # returns True or False
    def is_significant(self, token):
        return len(token) > 1 and not token in self.common and not \
               token.isdigit() and not '\\x' in token and not \
               "http//" in token and not "https//" in token 

    # Classifies a block of text.
    # text - the block to be classified
    # returns the classification, a string
    def check(self, text):
        # A text block is initially equally likely to be of any classification.
        era_guess = dict([(key, 1) for key in ERAS])
        type_guess = dict([(key, 1) for key in TYPES])

        # For each word in the block: 
        for token in set(text.split()):
            token = sub("[\[\]().,:!'\";-]", '', token.lower())
            # Ignore short and common words.
            if self.is_significant(token):
                # If we've seen the word before, note how often it's used for
                # each classification.
                if token in self.keywords:
                    for moc_era, frequency \
                        in self.keywords[token].era_freqs.iteritems():
                        era_guess[moc_era] *= max(1, frequency)
                    for moc_type, frequency \
                        in self.keywords[token].type_freqs.iteritems():
                        type_guess[moc_type] *= max(1, frequency)
                # Else add a new object for it to the keyword dict. 
                else:
                    self.keywords[token] = Keyword(token)
        
        # Guess which classification most likely applies to the text block and
        # ask the user to confirm or correct.
        era_res = max(era_guess, key = era_guess.get) 
        type_res = max(type_guess, key = type_guess.get)
        result = era_res + type_res

        if not self.auto:
            # If the guess was incorrect, get the correction and split it into
            # era and type.
            if raw_input("   %s? " % result) != "y":
                correction = raw_input("   Correction: ")
                era_cor = correction[:2]
                type_cor = correction[2:]

                # Update the frequencies now that we know the correct 
                # classification, unless the user wants to ignore the topic.
                if correction == result:
                    print "   No change."
                elif correction == "ignore":
                    print "   Ignoring topic."
                    result = "NA"
                elif correction in CLASSES:
                    result = correction
                    if era_cor != era_res:
                        if type_cor != type_res:
                            print "   Updating era and type."
                        else:
                            print "   Updating era."
                    else:
                        print "   Updating type."

                    for token in text.split():
                        token = sub("[\[\]().,:!'\";-]", '', token.lower())
                        if self.is_significant(token):
                            if era_cor != era_res:
                                self.keywords[token].era_freqs[era_cor] += 1
                            if type_cor != type_res:
                                self.keywords[token].type_freqs[type_cor] += 1
                # If the user made a typo, stick the topic in the misc
                # category so it can be manually indexed later.
                else:
                    print "   Invalid classification. Setting to \"SPall\"."
                    result = "SPall"
        else:
            print "   Classified as %s." % result

        return result

    # Removes insignificant tokens from the keyword dictionary.
    # returns the new dictionary
    def prune(self):
        # Make a shallow copy of the dictionary.
        ret_dict = dict(self.keywords)
        
        # Fetch the frequencies of each token.
        for token, frequencies in self.keywords.iteritems():
            era_values = frequencies.era_freqs.values()
            type_values = frequencies.type_freqs.values()

            # If there are more than three non-zero values, don't consider the
            # zeroes. (ignore outliers) (I made up this metric by eyeballing
            # values...)
            while 0 < era_values.count(0) < 4:
                era_values.remove(0)
            while 0 < type_values.count(0) < 2:
                type_values.remove(0)

            # If the variance is less than a quarter of the sum (I made up this
            # metric, too!), remove the token (assume it's just generally 
            # common among all topics). 
            era_mean = float(sum(era_values)) / len(era_values)
            type_mean = float(sum(type_values)) / len(type_values)
            era_variance = float(sum([(value - era_mean) ** 2 \
                           for value in era_values])) / len(era_values)
            type_variance = float(sum([(value - type_mean) ** 2 \
                            for value in type_values])) / len(type_values)

            if era_variance < float(sum(era_values)) / 4 \
               and type_variance < float(sum(type_values)) / 4:
                stderr.write("Removed %s.\n" % token)
                del ret_dict[token]
        return ret_dict

    def __exit__(self, exc_type, exc_value, traceback):
        pickle.dump(self.prune(), open("keywords.p", "wb"))
        pickle.dump(self.blacklist, open("ignorewords.p", "wb"))

if __name__ == "__main__":
    if raw_input("Reset classifications? ").lower == "y":
        os.system("mv keywords.p .keywords.p")
        os.system("mv ignorewords.p .ignorewords.p")
        print "Classification files hidden."
