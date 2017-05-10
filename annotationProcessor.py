# /Users/jacqueline/Desktop/All-TestGS-Output-5.5TH.tsv

from collections import defaultdict




class annotationProcessor(object):
    def __init__(self, data_set):
        self.data_set = data_set
        self._createDict()

    def _createDict(outputRows):
        lemma_dict = defaultdict(list)
        for row in outputRows:
            lemma = row.split("\t")[1]
            anglicism = row.split("\t")[6]
            evaluation = row.split("\t")[7]
            if anglicism == "Yes":
                if evaluation == "Correct":
                    label = "TrueP"
                else:
                    label = "FalseP"
            else:
                if evaluation == "Correct":
                    label = "TrueN"
                else:
                    label = "FalseN"
            lemma_dict[lemma].append(label)
        return lemma_dict

    def annotation_procces():
        f = open(data_set).readlines()[:5]
        lemma_dict = self._createDict(f)

        for key, evaluations in lemma_dict.items():
            if any(x.startswith("True") for x in evaluations):


        Accuracy = (TruePs + TrueNs) / float(TruePs + FalseNs + TrueNs + FalsePs)
        Precision = TruePs / float(TruePs + FalsePs)
        Recall =   TruePs / float(TruePs + FalseNs)


def main(argv):
    # Compute prior based on gold standard
    #transitions = getTransitions(goldTags, tags[0], tags[1])
    data = annotationProcessor(data_set)
    #eval.annotate(argv[1], file_ending)
    data.
    os.system('say "your program has finished"')
    #  Use an array of arguments?
    #  Should user pass in number of characters, number of languages, names of
    #  languages?

if __name__ == "__main__":
    main(sys.argv[1:]) # Skip over script name