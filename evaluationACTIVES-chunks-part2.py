import os
import io
import re
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()


def chunker(l, n):
    """Yield successive n-sized chunks from l."""
    words = []
    for i in range(0, len(l), n):
        words.append(l[i:i + n])
    return words


directory = "/Users/jacqueline/Google Drive/My_Data/Activ-es_Corpus/activ-es-v.01/corpus/plain/"
#directory = "/Users/jacqueline/Desktop/ACC/"
os.chdir(directory)

# create for manaual check
offFile = r"/Users/jacqueline/Google Drive/Dissertation/04Chapter2 Social Stratification/04Data/Anglicism Output/ACTIV-falseAngs.txt"
offText = io.open(offFile, encoding = "utf-8").readlines()
offList = [x.strip() for x in offText]

main_dict = Counter()
movieMetaData = []

for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".run") & file.startswith("es_A"):
            continue
        # split corpus into articles

        pattern = u"es_[^_]*_([^_]*)_([^_]*)_[^_]*_([^_]*)"
        metadata = list(re.search(pattern, file.decode('utf-8'), re.UNICODE).groups())
        text = io.open(file, encoding = "utf-8").read()
        words = toWordsCaseSen(text)
        #divide transcript into 20 segments
        chunk_size = len(words)/20
        chunks = chunker(words, chunk_size)
        for chunk in chunks:
            anglicisms = mixT.angList(chunk)
            anglicisms2 = [a for a in anglicisms if a not in offList]
            printList = '; '.join(anglicisms2)
            #print "Excluded:", [a for a in anglicisms if a in offList]
            #print "Anglicisms:", anglicisms2
            line_info = metadata + [len(chunk), len(anglicisms2), printList]
            movieMetaData.append(line_info)
            print line_info

with io.open('ACTIVchunks-angMetadata2.csv', 'w', encoding = "utf-8") as csv_file:
    csv_file.write(u"Year,Title,Genre,WordCount,AngCount,Angs\n")
    for row in movieMetaData:
        print row
        outputRow = u"{},{},{},{},{},{}\n".format(*row)
        csv_file.write(outputRow)

os.system('say "your program has finished"')


