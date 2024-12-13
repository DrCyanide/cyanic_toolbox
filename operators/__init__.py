from .filebrowser import FileBrowserOperator
from .faceimg2facemesh import FaceImg2FacemeshOperator
from .facemesh_cleanup import FacemeshCleanupOpenEyesOperator, FacemeshCleanupOpenMouthOperator, FacemeshCleanupSymmetrizeOperator, FacemeshCleanupSmartSymmetrizeOperator, FacemeshCleanupCloseEyesOperator, FacemeshCleanupCloseMouthOperator
from .rig_facemesh import RigFacemeshOperator, ParentFacemeshToRigOperator, AddRigOperator, GenRigFromMetaRigOperator
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
    RigFacemeshOperator,
    ParentFacemeshToRigOperator,
    AddRigOperator,
    GenRigFromMetaRigOperator,
    MocapOperator,
)