import os
import yaml

from hyperglot.languages import Languages as HGLanguages


class Languages(HGLanguages):
    loaded = set([])

    def __getitem__(self, item):
        orig = super().__getitem__(item)
        if item not in self.loaded:
            hyperglot_db = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "languages", item + ".yaml")
            )
            if os.path.isfile(hyperglot_db):
                with open(hyperglot_db) as file:
                    data = yaml.load(file, Loader=yaml.Loader)
                    orig.update(data)
            self.loaded.add(item)
        return orig
