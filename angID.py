# Anglicism Identifier by types
#  Evaluation.py
#  Using Python 2.7.11
# threshold approach
import sys
import re
import io
import os
from HiddenMarkovModel import HiddenMarkovModel
from nltk.tag.stanford import StanfordNERTagger
from collections import Counter
from CharNGram import *
from CodeSwitchedLanguageModel import CodeSwitchedLanguageModel
import pkg_resources

from pattern.es import parse as spnParse

""" Splits text input into words and formats them, splitting by whitespace

    @param text a string of text
    @return a list of formatted words
"""
# case-insensitive tokenizer for ngram probabilities only
print "Starting Program"

def toWords(text):  # separates punctuation
    # requires utf-8 encoding
    text = re.sub("www\.[^ ]*|https:\/\/[^ ]*", "WEBSITE", text)  # remove websites
    token = re.compile(ur'[\w]+|[^\s\w]', re.UNICODE)
    tokens = re.findall(token, text)
    return [word.lower() for word in tokens]
"""

def toWords(text): # splits on white space
    tokens = re.sub("\t|\n|\r", "", text)
    return [word.lower() for word in tokens.split()]
"""

def toWordsCaseSen(text): # separates punctuation
    # requires utf-8 encoding
    token = re.compile(ur'[\w]+|[^\s\w]', re.UNICODE)
    return re.findall(token, text)


# Return a transition matrix built from the gold standard
# Pass in tags for both languages


class mixedText:
    def __init__(self):
        self.cslm = self._setup()


    def _setup(self):
        n = 4

        resource_package = "anglicismIdentifier"  # Could be any module/package name
        Eng_resource_path = '/'.join(['TrainingCorpora', 'Subtlex.US.trim.txt'])
        engPath = pkg_resources.resource_filename(resource_package, Eng_resource_path)
        engData = toWords(io.open(engPath, 'r', encoding='utf8').read())

        Spn_resource_path = '/'.join(['TrainingCorpora', 'ActivEsCorpus.txt'])
        spnPath = pkg_resources.resource_filename(resource_package, Spn_resource_path)
        spnData = toWords(io.open(spnPath, 'r', encoding='utf8').read())


        enModel = CharNGram('Eng', getConditionalCounts(engData, n), n)
        esModel = CharNGram('Spn', getConditionalCounts(spnData, n), n)

        return CodeSwitchedLanguageModel([enModel, esModel])



    def tag(self, text_list):
        #annotation_lists = []
        hmm = HiddenMarkovModel(text_list, self.cslm)
        annotation_lists = zip(text_list, hmm.lemmas, hmm.lang, hmm.NE, hmm.ang, hmm.engProbs, hmm.spnProbs)
        return annotation_lists

    def angDict(self, text_list):
        hmm = HiddenMarkovModel(text_list, self.cslm)
        ang = ""
        ang_list = []
        for token, tag in zip(text_list, hmm.ang):
            if tag == "Yes":
                ang = " ".join([ang, token])
                continue
            else:
                if ang != "":
                    ang_list.append(ang.strip())
                    ang = ""
                    ang_lemma = ""
        return dict(Counter(ang_list))

    def angList(self, text_list):
        tags = [u"Eng", u"Spn"]
        hmm = HiddenMarkovModel(text_list, self.cslm)
        ang = ""
        ang_list = []
        for token, tag in zip(text_list, hmm.ang):
            if tag == "Yes":
                ang = " ".join([ang, token])
                continue
            else:
                if ang != "":
                    ang_list.append(ang.strip())
                    ang = ""
        return ang_list

    #  Tag testCorpus and write to output file
    def annotate(self, testCorpus):
        file_ending = "-2.tsv"
        print "Annotation Mode"
        with io.open(re.sub("\.txt$", "", testCorpus) + '-Annotated' +
                     file_ending, 'w', encoding='utf8') as output:
            text = io.open(testCorpus).read()
            testWords = toWordsCaseSen(text)
            tagged_rows = self.tag(testWords)
            # create anglicism output file

            output.write(u"Token\tLemma\tLanguage\tNamed Entity\tAnglicism\tEng-NGram Prob\tSpn-NGram Prob\n")

            ang = ""
            ang_lemma = ""
            ang_list = []
            lemma_dict = {}
            for row in tagged_rows:
                csv_row = '\t'.join([unicode(s) for s in row]) + u"\n"
                output.write(csv_row)
                if "Yes" in row:
                    ang = " ".join([ang, row[0]])
                    ang_lemma = " ".join([ang_lemma, row[1]])
                    continue
                else:
                    if ang != "":
                        ang_list.append(ang)
                        lemma_dict[ang] = ang_lemma
                        ang = ""
                        ang_lemma = ""

            # create anglicism output file
            angOutput = io.open(re.sub("\.tsv$", "", testCorpus) + '-English' +
                                 file_ending, 'w', encoding='utf8')
            angOutput.write(u"English Tokens\tLemma\tCount\n")
            ang_Counter = Counter(ang_list)
            ang_total = sum(ang_Counter.itervalues())
            for ang, count in ang_Counter.most_common():
                ang_row = '\t'.join([unicode(ang), unicode(count), unicode(lemma_dict[ang])]) + u"\n"
                angOutput.write(ang_row)
            angOutput.close()
            print "Annotation files written"
            print ang_total, "English tokens found"

    #  Evaluate goldStandard and write to output file
    def evaluate(self, goldStandard):
        file_ending = "-2.tsv"
        print "Evaluation Mode"
        with io.open(goldStandard.strip(".tsv") + '-Output' +
                     file_ending, 'w', encoding='utf8') as output:
            # create error file
            error_file = io.open(goldStandard.strip(".tsv") + '-Errors' +
                                 file_ending, 'w', encoding='utf8')
            error_file.write(
                u'Token\tGS\tLemma\tErrorType\tEngNgram\tSpnNgram\tNgramDifference\n')
            #create list of text and tags
            lines = io.open(goldStandard, 'r', encoding='utf8').readlines()
            text, gold_tags = [], []
            for x in lines:
                columns = x.split("\t")
                text.append(columns[-2].strip())
                gold_tags.append(columns[-1].strip())
            # annotate text with model
            annotated_output = self.tag(text)
            tokens, lemmas, lang_tags, NE_tags, anglicism_tags, engProbs, spnProbs = map(list, zip(*annotated_output))

            # set counters to 0
            TrueP = FalseN = TrueN = FalseP = 0
            evaluations = []

            # compare gold standard and model tags
            for index, tags in enumerate(zip(anglicism_tags, gold_tags)):
                ang = tags[0]
                gold = tags[1]
                if gold == "punc" or gold == "num":
                    evaluations.append("NA")
                    continue
                if ang == "Yes":
                    # is this token really  an anglicism?
                    if gold == 'Eng':
                        TrueP += 1  # yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseP += 1
                        evaluations.append("Incorrect")
                        # change lemma to show both lemmas
                        correctLemma = spnParse(tokens[index], lemmata=True)
                        lemmas[index] = lemmas[index] + "|" + correctLemma
                        # write to error file
                        try:
                            difference = engProbs[index] - spnProbs[index]
                        except TypeError:
                            difference = "NA"
                        error_info = [tokens[index], gold, lemmas[index], "FalseP", str(engProbs[index]), str(spnProbs[index]), str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
                else:   # if ang ==  'no'
                    # is this token really not an anglicism?
                    if gold != 'Eng':
                        TrueN += 1 #yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseN += 1
                        evaluations.append("Incorrect")
                        # change lemma to show both lemmas
                        correctLemma = spnParse(tokens[index], lemmata=True)
                        lemmas[index] = lemmas[index] + "|" + correctLemma
                        # write to error file
                        try:
                            difference = engProbs[index] - spnProbs[index]
                        except TypeError:
                            difference = "NA"
                        error_info = [tokens[index], gold, lemmas[index], "FalseN", str(engProbs[index]), str(spnProbs[index]), str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
            #write
            Accuracy = (TrueP + TrueN) / float(TrueP + FalseN + TrueN + FalseP)
            Precision = TrueP / float(TrueP + FalseP)
            Recall =   TrueP / float(TrueP + FalseN)
            fScore = 2*Precision*Recall/float(Precision + Recall)
            output.write(
                u"Accuracy: {}\nPrecision: {}\nRecall: {}\nF-Score: {}\n".format(
                    Accuracy, Precision, Recall, fScore))
            output.write(
                u"Token\tLemma\tGold Standard\tTagged Language\tNamed Entity\tAnglicism\tEvaluation\n")
            for all_columns in zip(text, lemmas, gold_tags, lang_tags, NE_tags, anglicism_tags, evaluations):
                output.write(u"\t".join(all_columns) + u"\n")
            print u"Accuracy\nPrecision\nRecall\nF-Score\n{}\n{}\n{}\n{}".format(
                    Accuracy, Precision, Recall, fScore)
            print "TrueP:", TrueP
            print "FalseP:", FalseP
            print "FalseN:", FalseN
            print "Evaluation file written"

"""
Process arguments
Get corpora and create NGram models
Create Code-Switch Language Model
Build Markov model with Expectation Minimization
Annotate
Evaluate
"""
# Evaluation.py goldStandard testCorpus
def main(argv):

    mixedT = mixedText()
    if argv[0] == '-a':
        mixedT.annotate(argv[1])
    elif argv[0] == '-e':
        mixedT.evaluate(argv[1])
    else:
        mixedT.annotate(argv[0])
        mixedT.evaluate(argv[1])
    os.system('say "your program has finished"')
    #  Use an array of arguments?
    #  Should user pass in number of characters, number of languages, names of
    #  languages?

if __name__ == "__main__":
    main(sys.argv[1:]) # Skip over script name
