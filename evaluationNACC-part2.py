import os
import io
import re
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()

directory = "/Users/jacqueline/Google Drive/My_Data/NACC_Corpus/"
os.chdir(directory)

# create for manaual check
offFile = r"/Users/jacqueline/Google Drive/Dissertation/04Chapter2 Social Stratification/04Data/Anglicism Output/NACC-falseAngs.txt"
offText = io.open(offFile, encoding = "utf-8").readlines()
offList = [x.strip() for x in offText]

main_dict = Counter()
articleMetaData = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.startswith("01NACC-"):
            continue
        # split corpus into articles
        newspaper = re.search("01NACC-(.*).txt", file).group(1)
        text = io.open(file, encoding = "utf-8").read()
        articles = text.split("START_FILE")
        for index, article in enumerate(articles):
            title = str(index + 1) + newspaper
            words = toWordsCaseSen(article)
            anglicisms = mixT.angList(words)
            anglicisms2 = [a for a in anglicisms if a not in offList]
            printList = '; '.join(anglicisms2)
            #print "Excluded:", [a for a in anglicisms if a in offList]
            #print "Anglicisms:", anglicisms2
            articleMetaData.append([title, newspaper, len(words), len(anglicisms2), printList])

with io.open('NACCangMetadata.csv', 'w', encoding = "utf-8") as csv_file:
    csv_file.write(u"Title,Newspaper,WordCount,AngCount,Angs\n")
    for row in articleMetaData:
        print row
        outputRow = u"{},{},{},{},{}\n".format(*row)
        csv_file.write(outputRow)

os.system('say "your program has finished"')


