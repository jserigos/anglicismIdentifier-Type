# HiddenMarkovModel.py
# Using Python 2.7.11
from collections import defaultdict
import math
import CodeSwitchedLanguageModel
import re
import io
from pattern.en import parse as engParse
from pattern.es import parse as spnParse
import os
import pkg_resources

resource_package = "anglicismIdentifier"  # Could be any module/package name

Eng_resource_path = '/'.join(['TrainingCorpora', 'EngDict.txt'])
EngPath = pkg_resources.resource_filename(resource_package, Eng_resource_path)
EngDict = io.open(EngPath, 'r', encoding='utf8').read().split("\n")

Spn_resource_path = '/'.join(['TrainingCorpora', 'lemario-20101017.txt'])
SpnPath = pkg_resources.resource_filename(resource_package, Spn_resource_path)
SpnDict = io.open(SpnPath, 'r', encoding='utf8').read().split("\n")

Spn_lemma_path = '/'.join(['TrainingCorpora','lemmatization-es.txt'])
SpnPath2 = pkg_resources.resource_filename(resource_package, Spn_lemma_path)
SpnLemmaList = io.open(SpnPath2, 'r', encoding='utf8').read().split("\n")

spLemmaDict = defaultdict(list)
for x in SpnLemmaList:
    try:
        a,b = x.split('\t')
        spLemmaDict[b].append(a)
    except ValueError:
        print x

class HiddenMarkovModel:
    def __init__(self, words, cslm):
        self.words = words
        self.cslm = cslm
        self.tagSet = [u"Eng", u"Spn"]
        self.lemmas = []
        self.lang = []
        self.NE = []
        self.ang = []
        self.engProbs = []
        self.spnProbs = []
        self._generateTags()


    def _generateTags(self):
        print "Tagging {} words".format(len(self.words))
        token = re.compile(ur'[^\w\s]', re.UNICODE)
        for k, word in enumerate(self.words):
            # determine NE
            if word[0].isupper():
                self.NE.append("NE")
                NE = "NE"
            else:
                self.NE.append("0")
                NE = "0"

            # annotate punct and move to next token
            if re.match(token, word):
                self.lang.append('Punct')
                self.ang.append('No')
                self.lemmas.append(word)
                self.engProbs.append("NA")
                self.spnProbs.append("NA")
                continue

            # annotate numbers and move to next token
            num = "no"
            for char in word:
                if char.isdigit():
                    num = "yes"
            if num == "yes":
                self.lang.append('Num')
                self.ang.append('No')
                self.lemmas.append(word)
                self.engProbs.append("NA")
                self.spnProbs.append("NA")
                continue

            # for lexical tokens determine lang tag
            spnProb = self.cslm.prob("Spn", word); self.spnProbs.append(spnProb)
            engProb = self.cslm.prob("Eng", word); self.engProbs.append(engProb)

            spnTokenParse = spnParse(word, lemmata=True)
            spnLemma = spnTokenParse.split("/")[4]
            spnLemmaList = spLemmaDict[word]
            engTokenParse = engParse(word, lemmata=True)
            engLemma = engTokenParse.split("/")[4]

            if 0 < engProb - spnProb < 5.5:
                if engLemma not in EngDict or spnLemmaList:
                    self.lemmas.append("|".join(spnLemmaList))
                    self.lang.append("Spn")
                    self.ang.append("No")
                elif spnLemma in SpnDict:
                    self.lemmas.append(spnLemma)
                    self.lang.append("Spn")
                    self.ang.append("No")
                else:
                    self.lemmas.append(engLemma)
                    self.lang.append("Eng")
                    if NE == "0":
                        self.ang.append("Yes")
                    else:
                        self.ang.append("No")
            else:
                lang = self.cslm.guess(word)
                self.lang.append(lang)
                if lang == "Eng":
                    self.lemmas.append(engLemma)
                    if NE == "0":
                        self.ang.append("Yes")
                    else:
                        self.ang.append("No")
                else:
                    self.lemmas.append("|".join(spnLemmaList))
                    self.ang.append("No")

