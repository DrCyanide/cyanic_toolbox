from .filebrowser import FileBrowserOperator
from .faceimg2facemesh import FaceImg2FacemeshOperator
from .facemesh_cleanup import FacemeshCleanupOpenEyesOperator, FacemeshCleanupOpenMouthOperator, FacemeshCleanupSymmetrizeOperator, FacemeshCleanupCloseEyesOperator, FacemeshCleanupCloseMouthOperator
from .rig_facemesh import RigFacemeshOperator, ParentFacemeshToRigOperator, AddRigOperator
from .mocap import GenRigFromMetaRigOperator, MocapOperator

operator_classes = (
    FileBrowserOperator,
    FaceImg2FacemeshOperator,
    FacemeshCleanupOpenEyesOperator,
    FacemeshCleanupOpenMouthOperator,
    FacemeshCleanupSymmetrizeOperator,
    FacemeshCleanupCloseEyesOperator,
    FacemeshCleanupCloseMouthOperator,
    RigFacemeshOperator,
    ParentFacemeshToRigOperator,
    AddRigOperator,
    GenRigFromMetaRigOperator,
    MocapOperator,
)