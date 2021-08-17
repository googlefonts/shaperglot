from hyperglot.languages import Languages as HGLanguages
import os
import yaml


class Languages(HGLanguages):
    loaded = set([])

    def __getitem__(self, item):
        orig = super(self.__class__, self).__getitem__(item)
        if item not in self.loaded:
            DB = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "languages", item + ".yaml")
            )
            if os.path.isfile(DB):
                with open(DB) as f:
                    data = yaml.load(f, Loader=yaml.Loader)
                    orig.update(data)
            self.loaded.add(item)
        return orig
