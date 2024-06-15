import pandas as pd

def makeLatexList(csvFile):
    """Takes a CSV file which has at least a 'Name' and an 'id' column and turns them into a Latex List"""
    data = pd.read_csv(csvFile, usecols=["Name", "id"])
    print("\\begin{itemize}[itemsep=.0125mm,parsep=2pt]")
    data = data.T
    for row in data:
        name = data[row]["Name"]
        name.replace("&", "\&")
        print("\t\item[\\textbf{{ {} }}] {}".format(data[row]["id"], name))
    print("\end{itemize}")

campsFile = "~/Downloads/camps_ids.csv"
artFile = "~/Downloads/art_ids.csv"
makeLatexList(campsFile)
makeLatexList(artFile)
