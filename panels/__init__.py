from .facemesh_builder_panel import FACEMESH_BUILDER_PT_Panel
from .facemesh_general_panel import FACEMESH_GENERAL_PT_Panel
from .facemesh_cleanup_panel import FACEMESH_CLEANUP_PT_Panel
from .facemesh_rigging_panel import FACEMESH_RIGGING_PT_Panel
from .mocap_panel import MOCAP_PT_Panel

panel_classes = (
    FACEMESH_BUILDER_PT_Panel,
    FACEMESH_GENERAL_PT_Panel,
    FACEMESH_CLEANUP_PT_Panel,
    FACEMESH_RIGGING_PT_Panel,
    MOCAP_PT_Panel,
)