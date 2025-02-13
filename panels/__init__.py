from .facemesh_general_panel import FACEMESH_GENERAL_PT_Panel
from .facemesh_builder_panel import FACEMESH_BUILDER_PT_Panel
from .facemesh_cleanup_panel import FACEMESH_CLEANUP_PT_Panel
from .facemesh_rigging_panel import FACEMESH_RIGGING_PT_Panel
from .eye_mgmt_panel import EYE_MGMT_PT_Panel
from .parts_mgmt_panel import PARTS_MGMT_PT_Panel
from .rigging_mgmt_panel import RIGGING_MGMT_PT_Panel
from .metarigging_panel import METARIGGING_PT_Panel
from .rigging_panel import RIGGING_PT_Panel
from .mocap_panel import MOCAP_PT_Panel

panel_classes = (
    FACEMESH_GENERAL_PT_Panel,
    FACEMESH_BUILDER_PT_Panel,
    FACEMESH_CLEANUP_PT_Panel,
    # FACEMESH_RIGGING_PT_Panel, # Depricated
    # EYE_MGMT_PT_Panel, # Depricated
    PARTS_MGMT_PT_Panel,
    RIGGING_MGMT_PT_Panel,
    METARIGGING_PT_Panel,
    RIGGING_PT_Panel,
    # MOCAP_PT_Panel,
)