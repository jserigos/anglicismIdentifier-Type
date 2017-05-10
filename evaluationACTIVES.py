import os
import io
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()

directory = "/Users/jacqueline/Google Drive/My_Data/Activ-es_Corpus/activ-es-v.01/corpus/plain/"
os.chdir(directory)

# create for manaual check

main_dict = Counter()
for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".run") & file.startswith("es_A"):
            continue
        text = io.open(file, encoding = "utf-8").read()
        words = toWordsCaseSen(text)
        a = Counter(mixT.angDict(words))
        main_dict.update(a)
        print "Finished {}, with {} anglicisms".format(file, len(a))


with io.open('ACTIVESangReviewList.csv', 'w', encoding = "utf-8") as csv_file:
    for key, value in main_dict.most_common():
        outputRow = u"{},{}\n".format(key, value)
        csv_file.write(outputRow)

os.system('say "your program has finished"')



