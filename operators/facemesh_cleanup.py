import bpy
import os
import json

# data_dir = 'data'
script_dir = os.path.dirname(__file__)
data_dir = os.path.join(os.path.split(script_dir)[0], 'data')
facemesh_mapping_file = os.path.join(data_dir, 'facemesh_rigify_mapping.json')
facemesh_config_data = {}

def load_config():
    global facemesh_config_data
    # with open(os.path.join(root_url, facemesh_mapping_file), 'r') as input_file:
    with open(facemesh_mapping_file, 'r') as input_file:
        string_format = input_file.read()
        facemesh_config_data = json.loads(string_format)

def findObjectByNameAndType(name, obj_type):
    objects = [obj for obj in bpy.context.scene.objects if obj.type == obj_type and obj.data.name == name]
    if len(objects) == 1:
        return objects[0]
    print('Found %s objects for %s, %s' % (len(objects), name, obj_type))
    print(objects)
    return objects[-1]

def selectObject(name, obj_type):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj = findObjectByNameAndType(name, obj_type)
    bpy.context.view_layer.objects.active = obj # Active object is what transform_apply is interacting with
    bpy.data.objects[obj.name].select_set(True)
    return obj


def delete_faces(facemesh, face_vert_list):
    selectObject(facemesh.name, 'MESH')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Counter-intuitively, you select the vertexes in Object mode, then switch to Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for vert in facemesh.vertices:
        vert.select = False

    for face in face_vert_list:
        for v in face:
            facemesh.vertices[v].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for v in face:
            facemesh.vertices[v].select = False


def delete_edges(facemesh, edge_vert_list):
    selectObject(facemesh.name, 'MESH')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Counter-intuitively, you select the vertexes in Object mode, then switch to Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for vert in facemesh.vertices:
        vert.select = False

    for face in edge_vert_list:
        for v in face:
            facemesh.vertices[v].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for v in face:
            facemesh.vertices[v].select = False

def rebuild_faces(facemesh, face_vert_list):
    selectObject(facemesh.name, 'MESH')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Counter-intuitively, you select the vertexes in Object mode, then switch to Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for vert in facemesh.vertices:
        vert.select = False

    for face in face_vert_list:
        for v in face:
            facemesh.vertices[v].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.material_slot_assign()
        # bpy.ops.mesh.f2()

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        for v in face:
            facemesh.vertices[v].select = False

class FacemeshCleanupSmartSymmetrizeOperator(bpy.types.Operator):
    """Symmetry by vertex. More precise than Blender's Symmetrize for the facemesh"""
    bl_idname = "object.facemeshcleanup_smart_symmetrize"
    bl_label = "FacemeshCleanupSmartSymmetrize"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()
        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        selectObject(facemesh.name, 'MESH')

        # Doing it simple for now
        #   * Assuming Mirroring over X

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')

        # Counter-intuitively, you select the vertexes in Object mode, then switch to Edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        for vert_index in facemesh_config_data['symmetry']['center']:
            # facemesh.vertices[vert_index].select = True
            facemesh.vertices[vert_index].co.x = 0
      
        for vert_pair in facemesh_config_data['symmetry']['mirror_pairs']:
            # Find the distance between the two X axis, split that distance left and right.
            # Average the Y and Z 
            left_side = facemesh.vertices[vert_pair[0]]
            right_side = facemesh.vertices[vert_pair[1]]

            x_distance = abs(left_side.co.x) + abs(right_side.co.x)
            facemesh.vertices[vert_pair[0]].co.x = -1 * x_distance/2
            facemesh.vertices[vert_pair[1]].co.x = x_distance/2

            z_average = (left_side.co.z + right_side.co.z) / 2
            facemesh.vertices[vert_pair[0]].co.z = z_average
            facemesh.vertices[vert_pair[1]].co.z = z_average

            y_average = (left_side.co.y + right_side.co.y) / 2
            facemesh.vertices[vert_pair[0]].co.y = y_average
            facemesh.vertices[vert_pair[1]].co.y = y_average


        bpy.ops.object.mode_set(mode=starting_mode)
        return {'FINISHED'}


class FacemeshCleanupSymmetrizeOperator(bpy.types.Operator):
    """Use Snap to Symmetry on the model. If it doesn't work right the first time, manually edit the verts to be more symmetrical and try again"""
    bl_idname = "object.facemeshcleanup_symmetrize"
    bl_label = "FacemeshCleanupSymmetrize"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations


    def execute(self, context):
        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        selectObject(facemesh.name, 'MESH')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.symmetry_snap()

        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode=starting_mode)
        return {'FINISHED'}

class FacemeshCleanupOpenEyesOperator(bpy.types.Operator):
    """Cutout the eye holes from the facemesh"""
    bl_idname = "object.facemeshcleanup_openeyes"
    bl_label = "FacemeshCleanupOpenEyes"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations


    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()

        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        delete_faces(facemesh, facemesh_config_data['face_verts']['eye.L'])
        delete_faces(facemesh, facemesh_config_data['face_verts']['eye.R'])

        delete_edges(facemesh, facemesh_config_data['edge_verts']['eye.L'])
        delete_edges(facemesh, facemesh_config_data['edge_verts']['eye.R'])

        bpy.ops.object.mode_set(mode=starting_mode)

        return {'FINISHED'}
    
class FacemeshCleanupCloseEyesOperator(bpy.types.Operator):
    """Fill the eye holes of the facemesh"""
    bl_idname = "object.facemeshcleanup_closeeyes"
    bl_label = "FacemeshCleanupCloseEyes"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()

        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        rebuild_faces(facemesh, facemesh_config_data['face_verts']['eye.L'])
        rebuild_faces(facemesh, facemesh_config_data['face_verts']['eye.R'])

        bpy.ops.object.mode_set(mode=starting_mode)

        return {'FINISHED'}

class FacemeshCleanupOpenMouthOperator(bpy.types.Operator):
    """Cutout the mouth from the facemesh"""
    bl_idname = "object.facemeshcleanup_openmouth"
    bl_label = "FacemeshCleanupOpenMouth"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations


    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()

        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        delete_faces(facemesh, facemesh_config_data['face_verts']['mouth'])

        delete_edges(facemesh, facemesh_config_data['edge_verts']['mouth'])

        bpy.ops.object.mode_set(mode=starting_mode)

        return {'FINISHED'}

class FacemeshCleanupCloseMouthOperator(bpy.types.Operator):
    """Fill the mouth of the facemesh"""
    bl_idname = "object.facemeshcleanup_closemouth"
    bl_label = "FacemeshCleanupCloseMouth"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations


    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()

        facemesh = context.scene.cyanic_facemesh
        starting_mode = bpy.context.object.mode

        rebuild_faces(facemesh, facemesh_config_data['face_verts']['mouth'])

        bpy.ops.object.mode_set(mode=starting_mode)

        return {'FINISHED'}