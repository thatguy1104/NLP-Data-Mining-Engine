from main.DJANGO_SYNC.synchronize import Synchronizer


class SYNC_SECTION():

    def synchronize_mongogb(self) -> None:
        """
            Synchronize SDG & IHE page data containing computed validation and predictions
        """
        obj = Synchronizer()
        obj.run(limit=0)
