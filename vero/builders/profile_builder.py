from vero.builders.base_builder import BaseBuilder
from vero.storage.storage_manager import StorageManager


class CompanyProfileBuilder(BaseBuilder):

    def __init__(self):

        self.storage = StorageManager()

    def build(self, company):

        website = self.storage.load_raw(company, "website")
        github = self.storage.load_raw(company, "github")
        news = self.storage.load_raw(company, "news")
        hiring = self.storage.load_raw(company, "hiring")
        funding = self.storage.load_raw(company, "funding")

        profile = {

            "company": company,

            "website": website,

            "github": github,

            "news": news,

            "hiring": hiring,

            "funding": funding

        }

        self.storage.save_profile(
            company,
            profile
        )

        return profile