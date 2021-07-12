from nltk.corpus import wordnet as wn
import csv

def get_keywords(word:str):
    keyword_list = []
    for ss in wn.synsets(word):
            for keywords in ss.lemma_names():
                if keywords.lower() != word:
                    keyword_list.append(keywords.lower())

    return keyword_list

with open("main/IHE_KEYWORDS/approach_keywords.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    headers = [row for row in reader][0]

keyword_matrix = []
for word in headers:
    readable_word = word.replace(" ", "_").lower()
    # print(word)
    if "_and_" in readable_word:
        keyword_list = []
        word_list = readable_word.split("_")
        word_list.remove("and")
        for words in word_list:
            for keywords in get_keywords(words):
                keyword_list.append(keywords)
        keyword_matrix.append(keyword_list)
    else:
        keyword_list = get_keywords(readable_word)
        keyword_matrix.append(keyword_list)
#     print(keyword_list)
# print(keyword_matrix)

longest_keyword_list = 0
for lists in keyword_matrix:
    if len(lists) > longest_keyword_list:
        longest_keyword_list = len(lists)
    
# print(longest_keyword_list)
list_strings = []
for rows in keyword_matrix:
    print(rows)
with open("main/IHE_KEYWORDS/approach_keywords.csv", "wt") as fp:
    writer = csv.writer(fp, delimiter=",")
    writer.writerow(headers)  # write header
    for list_index in range(0, longest_keyword_list):
        update_string = []
        for lists in keyword_matrix:
            #print(lists)
            if list_index < len(lists):
                update_string.append(lists[list_index].capitalize().replace("_", " "))
            else:
                update_string.append("")
        print("UPDATE STIRNG: ", update_string)
        writer.writerow(update_string)
        # update_string = update_string[:-1]
        # list_strings.append(update_string)

# with open("main/IHE_KEYWORDS/approach_keywords.csv", "wt") as fp:
#     writer = csv.writer(fp, delimiter=",")
#     writer.writerow(headers)  # write header
#     for rows in list_strings:
#         writer.writerow([rows.replace("\"", "")])
    #writer.writerows(list_strings)

# print("NOOOOO")
# for ss in wn.synsets('cardiovascular'):
#     print(ss)
#     print(ss.lemma_names())
#     print(ss.lemmas())

# for ss in wn.synsets('kidney_disease'):
#     print(ss)

# for ss in wn.synsets('kidney_disease'):
#     print(ss.lemma_names())
#     print(ss.lemmas())