import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def getFileData():
    files_directory = "GENERATED_FILES/"
    DIR = 'GENERATED_FILES'
    num_of_files = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    resulting_data = []
    for i in range(1, num_of_files):
        with open(files_directory + str(i) + ".json") as json_file:
            data = json.load(json_file)
            if data and data["SubjectAreas"]:
                print(i, data["SubjectAreas"])
    
    df = pd.DataFrame.from_records(resulting_data)

def graph(df):
    #create padding column from values for circles that are neither too small nor too large
    df["padd"] = 2.5 * (df.Count - df.Count.min()) / \
        (df.Count.max() - df.Count.min()) + 0.5
    fig = plt.figure()
    #prepare the axes for the plot - you can also order your categories at this step
    s = plt.scatter(sorted(df.Var1.unique()), sorted(
        df.Var2.unique(), reverse=True), s=0)
    s.remove
    #plot data row-wise as text with circle radius according to Count
    for row in df.itertuples():
        bbox_props = dict(boxstyle="circle, pad = {}".format(
            row.padd), fc="w", ec="r", lw=2)
        plt.annotate(str(row.Count), xy=(row.Var1, row.Var2), bbox=bbox_props,
                    ha="center", va="center", zorder=2, clip_on=True)

    #plot grid behind markers
    plt.grid(ls="--", zorder=1)
    #take care of long labels
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


# df = getFileData()
# graph(df)
getFileData()