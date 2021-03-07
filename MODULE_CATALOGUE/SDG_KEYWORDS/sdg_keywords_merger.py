import os
import pandas as pd
import glob

class SDGKeywordsMerger():
    @staticmethod
    def merge(output_file):
        dfs = [] # list of data frames
        input_files = ["MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords_Australasia.csv", "MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords_Australasia.csv", "MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords_Students.csv"]
        
        for input_file in input_files:
            df = pd.read_csv(input_file)
            for column in df.columns:
                keywords = df[column].str
                df[column] = df[column].str.lower() # lowercase keywords
                df[column] = df[column].str.strip() # strip trailing whitespaces
            dfs.append(df)
        df_merged = dfs.pop(0)
        
        frame = {}
        for column in df_merged:
            merged_keywords = pd.Index(df_merged[column]).dropna()
            for df in dfs:
                if column in df:
                    keywords = pd.Index(df[column]).dropna()
                    merged_keywords = merged_keywords.union(keywords)
            merged_keywords = merged_keywords.drop_duplicates()
            frame[column] = pd.Series(merged_keywords)

        output = pd.DataFrame(frame)
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, output_file)
        output.to_csv(output_path, index=False)

# Merge SDG keywords.
SDGKeywordsMerger().merge("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv")
