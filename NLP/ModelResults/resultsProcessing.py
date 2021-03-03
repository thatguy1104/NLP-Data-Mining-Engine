import json
import os


class ProcessResults():
    def __init__(self, threshold):
        self.threshold = threshold

    def process(self):
        tempcwd = os.getcwd()

        with open('training_results.json') as json_file:
            data = json.load(json_file)
            perplexity = data['Perplexity']
            docTopics = data['Document Topics']
            finalData = {}
            for module in docTopics:
                weights = docTopics[module]
                related = {}
                for i in range(len(weights)):
                    weights[i] = weights[i].replace('(', '').replace(')', '').replace(
                        '%', '').replace(' ', '').split(',')
                    sdgNum = weights[i][0]
                    with open('SDG.json') as json_file:
                        goalNames = json.load(json_file)
                        sdgPercentage = weights[i][1]
                        try:
                            sdgPercentage = float(sdgPercentage)
                        except:
                            sdgPercentage = 0.0
                        if sdgPercentage > self.threshold:
                            related[sdgNum] = goalNames[sdgNum]
                            customName = "Keywords for SDG " + sdgNum
                            related[customName] = {}
                            related[customName] = data['Topic Words'][sdgNum]
                    finalData[module] = related
            file_name = "processed_results.json"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'w') as outfile:
                json.dump(finalData, outfile)
            os.chdir(tempcwd)


# results = ProcessResults(threshold=10)
# results.process()
