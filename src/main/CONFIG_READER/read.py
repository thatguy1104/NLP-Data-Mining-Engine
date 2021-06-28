# from configparser import ConfigParser
import configparser

def get_details(field, detail):
    config = configparser.ConfigParser()
    config.read("../config.ini")
    return config[field][detail]