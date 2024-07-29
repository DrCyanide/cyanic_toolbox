# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
import subprocess
import os
import sys
import importlib
from collections import namedtuple

from .operators import *
from .panels import *

bl_info = {
    "name" : "Cyanic Toolbox",
    "author" : "DrCyanide",
    "description" : "",
    "blender" : (2, 81, 0), # Minimum version
    "version" : (0, 5, 3), # Add-on version
    "location" : "View3D > Sidebar > Cyanic",
    "warning" : "Requires installation of dependencies",
    "tracker_url": "https://github.com/DrCyanide/cyanic_toolbox/issues",
    "doc_url": "https://github.com/DrCyanide/cyanic_toolbox/",
    "category" : "Generic"
}

# The dependency install code is based off of this github example
# https://github.com/robertguetzkow/blender-python-examples/blob/4a3c99a843305b91e05db386559905b23cf6eb87/add-ons/install-dependencies/install-dependencies.py
# And off of BlendARMocap's dependencies list
# https://github.com/cgtinker/BlendArMocap/blob/ecb4c91c01befbe29b75196eb72321867810ddf0/src/cgt_mediapipe/cgt_mp_preferences.py#L53
Dependency = namedtuple("Dependency", ["module", "package", "name"])
dependencies = (
    Dependency(module="numpy", package="numpy==1.26.4", name='np'), # numpy 2.0 had just released, and wasn't compatible with mediapipe yet
    Dependency(module="skimage", package="scikit-image", name=None),
    Dependency(module="cv2", package="opencv-python", name=None),
    Dependency(module="mediapipe", package=None, name=None),
)

dependencies_installed = False

def install_pip():
    """
    Installs pip if not already present. Please note that ensurepip.bootstrap() also calls pip, which adds the
    environment variable PIP_REQ_TRACKER. After ensurepip.bootstrap() finishes execution, the directory doesn't exist
    anymore. However, when subprocess is used to call pip, in order to install a package, the environment variables
    still contain PIP_REQ_TRACKER with the now nonexistent path. This is a problem since pip checks if PIP_REQ_TRACKER
    is set and if it is, attempts to use it as temp directory. This would result in an error because the
    directory can't be found. Therefore, PIP_REQ_TRACKER needs to be removed from environment variables.
    :return:
    """

    try:
        # Check if pip is already installed
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip

        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)


def import_module(module_name, global_name, reload=True):
    """
    Import a module.
    :param module_name: Module to import.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
        This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
        the global_name under which the module can be accessed.
    :raises: ImportError and ModuleNotFoundError
    """
    if global_name is None:
        global_name = module_name
    
    if global_name in globals():
        importlib.reload(globals()[global_name])
    else:
        # Attempt to import the module and assign it to globals dictionary. This allow to access the module under
        # the given name, just like the regular import would.
        globals()[global_name] = importlib.import_module(module_name)


def install_and_import_module(module_name, package_name=None, global_name=None):
    """
    Installs the package through pip and attempts to import the installed module.
    :param module_name: Module to import.
    :param package_name: (Optional) Name of the package that needs to be installed. If None it is assumed to be equal
        to the module_name.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
        This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
        the global_name under which the module can be accessed.
    :raises: subprocess.CalledProcessError and ImportError
    """
    if package_name is None or len(package_name) == 0:
        package_name = module_name
    if global_name is None or len(package_name) == 0:
        global_name = module_name

    
    # Blender disables the loading of user site-packages by default. However, pip will still check them to determine
    # if a dependency is already installed. This can cause problems if the packages is installed in the user
    # site-packages and pip deems the requirement satisfied, but Blender cannot import the package from the user
    # site-packages. Hence, the environment variable PYTHONNOUSERSITE is set to disallow pip from checking the user
    # site-packages. If the package is not already installed for Blender's Python interpreter, it will then try to.
    # The paths used by pip can be checked with `subprocess.run([bpy.app.binary_path_python, "-m", "site"], check=True)`

    # Create a copy of the environment variables and modify them for the subprocess call
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"

    subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, env=environ_copy)

    # The installation succeeded, attempt to import the module again
    import_module(module_name, global_name)

    # Update the installed dependencies table


def uninstall_module(module_name, package_name='', global_name=''):
    # Same idea as install, just with different pip args
    if len(package_name) == 0:
        package_name = module_name
    if len(global_name) == 0:
        global_name = module_name
    # Create a copy of the environment variables and modify them for the subprocess call
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"

    # Need to scan package name for '==', because that's only to install the correct 
    if '==' in package_name:
        package_name = package_name.split('==')[0]

    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package_name], check=True, env=environ_copy) 
    except subprocess.CalledProcessError as e:
        # Keep getting a exit status of 2, even though it's working correctly.
        pass
    
    # Remove the dependency from the imports
    del globals()[global_name]


class CYANIC_OT_install_dependencies(bpy.types.Operator):
    bl_idname = "cyanic.install_dependencies"
    bl_label = "Install all dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is requred. Blender may have to be started with "
                      "elevated permissions ('Run as administrator') in order to install"
                      )
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate when dependencies have been installed
        return not dependencies_installed
    
    def execute(self, context):
        try:
            install_pip()
            for dependency in dependencies:
                install_and_import_module(module_name=dependency.module,
                                          package_name=dependency.package,
                                          global_name=dependency.name)
                
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({'ERROR'}, str(err))
            return {"CANCELLED"}
        
        global dependencies_installed
        dependencies_installed = True

        # The example had this re-registering 
        for cls in operator_classes:
            bpy.utils.register_class(cls)
        for cls in panel_classes:
            bpy.utils.register_class(cls)

        return {"FINISHED"}

class CYANIC_OT_install_single_dependency(bpy.types.Operator):
    bl_idname = "cyanic.install_single_dependency"
    bl_label = "Install"
    bl_description = "Install a single dependency"
    bl_options = {"REGISTER", "INTERNAL"} # IDK if this is needed or not

    # dependency = None
    module_name : bpy.props.StringProperty('')
    package_name : bpy.props.StringProperty('')
    global_name : bpy.props.StringProperty('')

    def execute(self, context):
        if self.module_name is None or len(self.module_name) == 0:
            return {'CANCELLED'}
        try:
            install_and_import_module(module_name=self.module_name,
                                      package_name=self.package_name,
                                      global_name=self.global_name)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({'ERROR'}, str(err))
            return {"CANCELLED"}
        return {'FINISHED'}
    
class CYANIC_OT_uninstall_single_dependency(bpy.types.Operator):
    bl_idname = "cyanic.uninstall_single_dependency"
    bl_label = "Uninstall"
    bl_description = "Uninstall a single dependency"
    bl_options = {"REGISTER", "INTERNAL"} # IDK if this is needed or not

    dependency = None
    module_name : bpy.props.StringProperty('')
    package_name : bpy.props.StringProperty('')
    global_name : bpy.props.StringProperty('')

    def execute(self, context):
        if self.module_name is None or len(self.module_name) == 0:
            return {'CANCELLED'}
        try:
            uninstall_module(module_name=self.module_name,
                             package_name=self.package_name,
                             global_name=self.global_name)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({'ERROR'}, str(err))
            return {"CANCELLED"}
        return {'FINISHED'}


class CYANIC_PT_warning_panel(bpy.types.Panel):
    bl_label = "Warning"
    bl_category = "Cyanic"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        return not dependencies_installed
    
    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for the \"{bl_info.get('name')}\" add-on.",
                 f"1. Open the preferences (Edit > Preferences > Add-ons).",
                 f"2. Search for the \"{bl_info.get('name')}\" add-on.",
                 f"3. Open the details section of the add-on.",
                 f"4. Click on the \"{CYANIC_OT_install_dependencies.bl_label}\" button.",
                 f"   This will download and install the missing Python packages",
                 f"   if Blender has the required permissions. Run as Administrator,",
                 f"   or try using the portable version of Blender.",
                 f"",
                 f"If you're attempting to run the add-on from the text editor, ",
                 f"you won't see the options described above. Please install",
                 f"the add-on properly through the preferences.",
                 f"1. Open the add-on preferences (Edit > Preferences > Add-ons).",
                 f"2. Press the \"Install\" button.",
                 f"3. Search for the add-on file.",
                 f"4. Confirm the selection by pressing the \"Install Add-on\" button in the file browser."]
        
        for line in lines:
            layout.label(text=line)

class CYANIC_preferences(bpy.types.AddonPreferences):
    # The preferences in Preferences > Add-ons > Cyanic Toolbox
    bl_idname = __name__

    header_names = ["Module", "Version", ""]

    save_dir: bpy.props.EnumProperty(
        items=[
            ('IMG_DIR', 'With image file', 'Save in the same directory as the image.'),
            ('BLEND_DIR', 'With .blend file', 'Save in the same directory as the .blend file. If .blend file isn\'t saved, save with image.'),
            ('CUSTOM_DIR', 'Custom directory', 'Pick a custom directory to save in')
        ],
        name='Face mesh save dir',
        description='Set the default location where meshes created should be saved.',
        default='IMG_DIR'
    )

    custom_path: bpy.props.StringProperty(name='Custom Path', default='', subtype="FILE_PATH")

    def draw_dependency(self, dependency, dependency_box):
        # module name, version, install/remove button
        # Check if installed
        installed = False
        package_name = dependency.package
        global_name = dependency.module
        if dependency.name is not None:
            global_name = dependency.name
        if dependency.package is None:
            package_name = ''
        if global_name in globals():
            installed = True

        _d_box = dependency_box.box()
        box_split = _d_box.split()
        cols = [box_split.column(align=False) for _ in range(len(CYANIC_preferences.header_names))]
        # Module Name
        cols[0].label(text=dependency.module)

        # Version
        if installed:
            cols[1].label(text=globals()[global_name].__version__)
        else:
            cols[1].label(text='Not Installed')

        # Install/Remove button
        if installed:
            operator = cols[-1].operator(CYANIC_OT_uninstall_single_dependency.bl_idname)
            operator.module_name = dependency.module
            operator.package_name = package_name
            # No global name needed
        else:
            operator = cols[-1].operator(CYANIC_OT_install_single_dependency.bl_idname)
            operator.module_name = dependency.module
            operator.package_name = package_name
            operator.global_name = global_name

    def draw(self, context):
        layout = self.layout

        # Save dir
        layout.label(text="Set first choices for face mesh save directory. If .blend file isn't saved, custom path will be tried.")
        layout.prop(self, 'save_dir')
        layout.prop(self, 'custom_path')
        
        # Dependency sub-box
        dependency_box = layout.box()
        dependency_box.label(text="Add-on Dependencies")

        # Install All Dependencies button
        dependency_box.operator(CYANIC_OT_install_dependencies.bl_idname, icon="CONSOLE")

        # Dependency Table
        headers = dependency_box.split()
        for name in CYANIC_preferences.header_names:
            col = headers.column()
            col.label(text=name)
        for dependency in dependencies:
            self.draw_dependency(dependency, dependency_box)

        

# Classes used to set up the Add-on preferences / install messages
# I'd like to move these to their own files, but the shared global variables need consideration
preference_classes = [
    CYANIC_PT_warning_panel,
    CYANIC_OT_install_dependencies,
    CYANIC_OT_install_single_dependency,
    CYANIC_OT_uninstall_single_dependency,
    CYANIC_preferences,
]


# ------------------------------------------------
# That's the end of the Add-on preferences.
# Everything below here should be for prop definitions
# ------------------------------------------------


def armature_bone_count_match(_, obj):
    rigify_bone_count = 159 # How many bones a rigify rig has.
    # return len(obj.bones) == rigify_bone_count
    return obj.users > 0 and len(obj.bones) == rigify_bone_count

def facemesh_vertex_count_match(_, obj):
    facemesh_vertices_count = 468 # How many verticies a facemesh should have
    # return len(obj.vertices) == facemesh_vertices_count
    return obj.users > 0 and len(obj.vertices) >= facemesh_vertices_count # Went with >= incase the user extends the mesh to add more verts. Program will break with less verts, but not more

def armature_face_bones_match(_, obj):
    manditory_bones = ["eye.L", "eye.R", "jaw", "jaw.L", "jaw.L.001", "jaw.R", "jaw.R.001", "temple.L", "temple.R", "chin", "chin.001", "chin.L", "chin.R", "lip.B.L", "lip.B.L.001", "lip.B.R", "lip.B.R.001", "lip.T.L", "lip.T.L.001", "lip.T.R", "lip.T.R.001", "cheek.B.L", "cheek.B.L.001", "cheek.B.R", "cheek.B.R.001", "cheek.T.L", "cheek.T.L.001", "cheek.T.R", "cheek.T.R.001", "brow.T.L", "brow.T.L.001", "brow.T.L.002", "brow.T.L.003", "brow.T.R", "brow.T.R.001", "brow.T.R.002", "brow.T.R.003", "forehead.L", "forehead.L.001", "forehead.L.002", "forehead.R", "forehead.R.001", "forehead.R.002", "nose", "nose.001", "nose.002", "nose.003", "nose.004", "nose.L", "nose.L.001", "nose.R", "nose.R.001", "lid.B.L", "lid.B.L.001", "lid.B.L.002", "lid.B.L.003", "lid.T.L", "lid.T.L.001", "lid.T.L.002", "lid.T.L.003", "lid.B.R", "lid.B.R.001", "lid.B.R.002", "lid.B.R.003", "lid.T.R", "lid.T.R.001", "lid.T.R.002", "lid.T.R.003", "brow.B.L", "brow.B.L.001", "brow.B.L.002", "brow.B.L.003", "brow.B.R", "brow.B.R.001", "brow.B.R.002", "brow.B.R.003" ]
    for bone_name in manditory_bones:
        bone_id = obj.bones.find(bone_name)
        if bone_id is None or bone_id < 0:
            return False
    return True

def valid_metarig(_, obj):
    return obj.users > 0 and 'rigify_target_rig' in dir(obj) and armature_face_bones_match(_, obj)


def register():
    bpy.types.Scene.cyanic_img_path = bpy.props.StringProperty(
        name='Face Image',
        description='Path to an image that will be converted to a face mesh',
        subtype="FILE_PATH",
        # default="*.jpg;*.jpg"
    )

    bpy.types.Scene.cyanic_facemesh = bpy.props.PointerProperty(
        name="FaceMesh",
        description="FaceMesh generated from Mediapipe",
        type=bpy.types.Mesh,
        poll=facemesh_vertex_count_match
    )

    bpy.types.Scene.cyanic_eye_left = bpy.props.PointerProperty(
        name="Left Eye",
        description="The character's left eye",
        type=bpy.types.Mesh,
    )

    bpy.types.Scene.cyanic_eye_right = bpy.props.PointerProperty(
        name="Right Eye",
        description="The character's right eye",
        type=bpy.types.Mesh,
    )

    bpy.types.Scene.cyanic_rigify_rig = bpy.props.PointerProperty(
        name="Metarig",
        description="Rigify rig",
        type=bpy.types.Armature,
        poll=valid_metarig
    )

    bpy.types.Scene.cyanic_rigify_gen_rig = bpy.props.PointerProperty(
        name="Rig",
        description="Rigify generated rig",
        type=bpy.types.Armature,
        # poll=???,
    )

    bpy.types.Scene.cyanic_source_type = bpy.props.EnumProperty(
        name="Source",
        items=[
            ('image_mode', 'Image', 'Copy pose from from image'),
            ('video_mode', 'Video', 'Copy animation from video'),
        ],
        # default='img_mode'
    )

    bpy.types.Scene.cyanic_source_input = bpy.props.EnumProperty(
        name="Input",
        items=[
            ('file_input', 'File', 'Load file for mocap'),
            ('webcam_input', 'Webcam', 'Use webcam for mocap'),
        ],
        # default='img_mode'
    )

    bpy.types.Scene.cyanic_mocap_file_path = bpy.props.StringProperty(
        name='Image/Video',
        description='Path to an image/video that will be converted to a pose/animation',
        subtype="FILE_PATH",
    )

    global dependencies_installed
    dependencies_installed = False

    for cls in preference_classes:
        bpy.utils.register_class(cls)

    try:
        for dependency in dependencies:
            import_module(module_name=dependency.module, global_name=dependency.name)
        dependencies_installed = True
    except ModuleNotFoundError:
        # Don't continue registering
        return

    for cls in operator_classes:
        bpy.utils.register_class(cls)
    for cls in panel_classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.cyanic_img_path
    del bpy.types.Scene.cyanic_facemesh
    del bpy.types.Scene.cyanic_eye_left
    del bpy.types.Scene.cyanic_eye_right
    del bpy.types.Scene.cyanic_rigify_rig
    del bpy.types.Scene.cyanic_rigify_gen_rig

    del bpy.types.Scene.cyanic_source_type
    del bpy.types.Scene.cyanic_source_input
    del bpy.types.Scene.cyanic_mocap_file_path

    for cls in preference_classes:
        bpy.utils.unregister_class(cls)

    for cls in operator_classes:
        bpy.utils.unregister_class(cls)
    for cls in panel_classes:
        bpy.utils.unregister_class(cls)
