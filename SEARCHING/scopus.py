import json
import os

files_directory = "../SCOPUS/GENERATED_FILES/"
DIR = '../SCOPUS/GENERATED_FILES'
num_of_files = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
print(num_of_files)