from .no_orphaned_marks import NoOrphanedMarksCheck
from .orthographies import OrthographiesCheck
from .shaping_differs import ShapingDiffersCheck
from .unencoded_variants import UnencodedVariantsCheck

checks = [
    OrthographiesCheck,
    ShapingDiffersCheck,
    NoOrphanedMarksCheck,
    UnencodedVariantsCheck,
]
checks_map = {cls.name: cls for cls in checks}
schemas = {cls.name: cls.schema for cls in checks}
