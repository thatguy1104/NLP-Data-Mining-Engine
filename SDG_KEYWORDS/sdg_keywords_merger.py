import pandas as pd

class SDGKeywordsMerger():
    def merge(self):
        """
            Merge SDG-specific keywords compiled from 3 different sources:
                - SDG_Keywords_Australasia.csv stores the keywords compiled by a number of universities in Australia and New Zealand.
                - SDG_Keywords_Leicester.csv stores the keywords compiled by Leicester University.
                - SDG_Keywords_Students.csv stores the keywords compiled by the students working on the UCL5 MieMie v3 project.
        """
        sdg_keywords_australasia = "SDG_KEYWORDS/SDG_Keywords_Australasia.csv"
        sdg_keywords_leicester = "SDG_KEYWORDS/SDG_Keywords_Leicester.csv"
        sdg_keywords_students = "SDG_KEYWORDS/SDG_Keywords_Students.csv"

        input_files = [sdg_keywords_australasia, sdg_keywords_leicester, sdg_keywords_students]
        output_file = "SDG_KEYWORDS/SDG_Keywords.csv"
        
        dfs = [] # list of dataframe objects.
        for input_file in input_files:
            df = pd.read_csv(input_file)
            for column in df.columns:
                keywords = df[column].str
                df[column] = df[column].str.lower() # lowercase keywords.
                df[column] = df[column].str.strip() # strip any trailing whitespaces.
            dfs.append(df)
        df_merged = dfs.pop(0)
        
        frame = {}
        for column in df_merged:
            merged_keywords = pd.Index(df_merged[column]).dropna()
            for df in dfs:
                if column in df:
                    keywords = pd.Index(df[column]).dropna()
                    merged_keywords = merged_keywords.union(keywords)
            merged_keywords = merged_keywords.drop_duplicates() # remove duplicate keywords that appear in any particular SDG.
            frame[column] = pd.Series(merged_keywords)

        output = pd.DataFrame(frame)
        output.to_csv(output_file, index=False) # output merged keywords as a csv file.