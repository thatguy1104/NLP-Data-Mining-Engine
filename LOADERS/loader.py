class Loader():
    
    def load(self, count):
        raise NotImplementedError

    def load_pymongo_db(self):
        raise NotImplementedError

    def load_prediction_results(self):
        raise NotImplementedError