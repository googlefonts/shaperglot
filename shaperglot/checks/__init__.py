from .orthographies import OrthographiesCheck
from .shaping_differs import ShapingDiffersCheck
from .no_orphaned_marks import NoOrphanedMarksCheck
from strictyaml import Seq, Map

checks     = [ OrthographiesCheck, ShapingDiffersCheck, NoOrphanedMarksCheck ]
checks_map = { cls.name: cls for cls in checks }
schemas    = { cls.name: cls.schema for cls in checks }

