"""
    Standalone file to help with generation of approach keywords to be used with string match
    Manual inspection will have to be done on the keywords list once generated
"""

from nltk.corpus import wordnet as wn
import csv

def get_keywords(word: str) -> list:
    """
        Gets words associated with the one passed as an argument
    """

    keyword_list = []
    for ss in wn.synsets(word):
        for keywords in ss.lemma_names():
            if keywords.lower() != word:
                keyword_list.append(keywords.lower())

    return keyword_list

def get_headers() -> list:
    """
        Gets the headers from the existing approach keywords file
    """

    with open("main/IHE_KEYWORDS/approaches.csv") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        headers = [row for row in reader][0]
    return headers


def generate_keyword_matrix(headers: list) -> list:
    """
        Splits up the headers where there are more than one components of an approach
        Collects all the keywords for those split up headers to return a matrix
    """

    keyword_matrix = []
    for word in headers:
        readable_word = word.replace(" ", "_").lower()
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

    return keyword_matrix


def get_longest_keyword_list(keyword_matrix: list) -> int:
    """
        Calculates the longest keyword list in preparation to make the dataframe
    """

    longest_keyword_list = 0
    for lists in keyword_matrix:
        if len(lists) > longest_keyword_list:
            longest_keyword_list = len(lists)
    return longest_keyword_list
    

def write_results(headers: list, keyword_matrix: list, longest_keyword_list: int) -> None:
    """
        Writes the generated keywords to a new csv file
    """

    with open("main/IHE_KEYWORDS/approach_keywords_new.csv", "wt") as fp: # write to new file so can compare to previous
        writer = csv.writer(fp, delimiter=",")
        writer.writerow(headers)  # write header
        for list_index in range(0, longest_keyword_list):
            update_string = []
            for lists in keyword_matrix:
                if list_index < len(lists):
                    update_string.append(lists[list_index].capitalize().replace("_", " "))
                else:
                    update_string.append("")
            writer.writerow(update_string)


def main():
    headers = get_headers()
    keyword_matrix = generate_keyword_matrix(headers)
    longest_keyword_list = get_longest_keyword_list(keyword_matrix)
    write_results(headers, keyword_matrix, longest_keyword_list)


if __name__ == "__main__":
    main()