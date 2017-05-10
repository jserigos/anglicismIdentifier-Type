import os
import io
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()

directory = "/Users/jacqueline/Desktop/NACC"
os.chdir(directory)

# create for manaual check

main_dict = Counter()
for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".corpus"):
            continue
        # split corpus into articles
        text = io.open(file, encoding = "utf-8").read()
        words = toWordsCaseSen(text)
        a = Counter(mixT.angDict(words))
        main_dict.update(a)
        print "Finished {}, with {} anglicisms".format(file, len(a))


with io.open('angReviewList.csv', 'w', encoding = "utf-8") as csv_file:
    for key, value in main_dict.most_common():
        outputRow = u"{},{}\n".format(key, value)
        csv_file.write(outputRow)

os.system('say "your program has finished"')



