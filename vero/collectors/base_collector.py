from abc import ABC, abstractmethod

from vero.storage.storage_manager import StorageManager


class BaseCollector(ABC):

    def __init__(self):

        self.storage = StorageManager()

    @property
    @abstractmethod
    def source_name(self):
        """
        website
        github
        news
        funding
        etc.
        """
        pass

    @abstractmethod
    def collect(self, company):
        """
        Return a dictionary of collected data.
        """
        pass

    def run(self, company):

        print(f"\nCollecting {self.source_name}...")

        data = self.collect(company)

        self.storage.save_raw(
            company,
            self.source_name,
            data
        )

        print("Done.")

        return data