import json
import os

def rename():
    path = "GENERATED_FILES"
    files = os.listdir(path)
    for index, file in enumerate(files):
        header = file.split('.')[0]
        try:
            header = int(header)
            with open(path + "/" + file) as json_file:
                eid = json.load(json_file)['EID']
                print(header, path + "/" + eid + '.json')
                os.rename(path + "/" + file, path + "/" + eid + '.json')
        except:
            pass
