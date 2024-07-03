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

from .operators import *
from .panels import *

bl_info = {
    "name" : "Cyanic Toolbox",
    "author" : "DrCyanide",
    "description" : "",
    "blender" : (2, 80, 0), # Minimum version
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

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

    for cls in operator_classes:
        bpy.utils.unregister_class(cls)
    for cls in panel_classes:
        bpy.utils.unregister_class(cls)
