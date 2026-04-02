from .filebrowser import FileBrowserOperator
from .faceimg2facemesh import FaceImg2FacemeshOperator
from .facemesh_cleanup import FacemeshCleanupOpenEyesOperator, FacemeshCleanupOpenMouthOperator, FacemeshCleanupSymmetrizeOperator, FacemeshCleanupSmartSymmetrizeOperator, FacemeshCleanupCloseEyesOperator, FacemeshCleanupCloseMouthOperator
from .facemesh_default import FacemeshDefaultOperator
from .rig_facemesh import RigFacemeshOperator, ParentFacemeshToRigOperator, AddRigOperator, GenRigFromMetaRigOperator, ParentMouthToRigOperator
from .rig_hands import RigHandsOperator
from .eye_tools import MoveEyesToSocketsOperator, ParentEyesToRigOperator
from .mocap import MocapOperator

operator_classes = (
    FileBrowserOperator,
    FaceImg2FacemeshOperator,
    FacemeshCleanupOpenEyesOperator,
    FacemeshCleanupOpenMouthOperator,
    FacemeshCleanupSymmetrizeOperator,
    FacemeshCleanupSmartSymmetrizeOperator,
    FacemeshCleanupCloseEyesOperator,
    FacemeshCleanupCloseMouthOperator,
    FacemeshDefaultOperator,
    RigFacemeshOperator,
    ParentFacemeshToRigOperator,
    AddRigOperator,
    GenRigFromMetaRigOperator,
    ParentMouthToRigOperator,
    RigHandsOperator,
    MoveEyesToSocketsOperator,
    ParentEyesToRigOperator,
    MocapOperator,
)