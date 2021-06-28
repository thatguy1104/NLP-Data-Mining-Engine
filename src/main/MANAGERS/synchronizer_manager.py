from main.DJANGO_SYNC.synchronize import Synchronizer
from main.DJANGO_SYNC.raw_synchronize import RawSynchronizer


class SYNC_SECTION():

    def synchronize_mongo_PREMODEL(self) -> None:
        """
            Synchronize raw publication and module data after scrape (prior to NLP section)
        """
        obj = RawSynchronizer()
        obj.run()

    def synchronize_mongodb_POSTMODEL(self) -> None:
        """
            Synchronize SDG & IHE page data containing computed validation and predictions
        """
        obj = Synchronizer()
        obj.run(limit=0)

