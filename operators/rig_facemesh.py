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

class AddRigOperator(bpy.types.Operator):
    """Add a Rigify Meta-Rig to the scene"""
    bl_idname = "object.add_rig"
    bl_label = "AddRig"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        # Add Rig
        bpy.ops.object.armature_human_metarig_add()
        scene_armatures = bpy.data.armatures
        context.scene.cyanic_rigify_rig = scene_armatures[-1]
        # armature = context.scene.cyanic_rigify_rig
        return {'FINISHED'}


class RigFacemeshOperator(bpy.types.Operator):
    """Align the Rigify face bones to the facemesh. If eyes are selected, their bones will be lined up too"""
    bl_idname = "object.rig_facemesh"
    bl_label = "RigFacemesh"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            load_config()
        
        facemesh = context.scene.cyanic_facemesh
        armature = context.scene.cyanic_rigify_rig
        
        if armature is None:
            # Add Rig
            bpy.ops.object.armature_human_metarig_add()
            scene_armatures = bpy.data.armatures
            context.scene.cyanic_rigify_rig = scene_armatures[-1]
            armature = context.scene.cyanic_rigify_rig

        starting_mode = bpy.context.object.mode

        armature_obj = selectObject(armature.name, 'ARMATURE')
        armature_world_matrix_inverted = armature_obj.matrix_world.inverted()
        bpy.ops.object.mode_set(mode='EDIT')

        facemesh_obj = findObjectByNameAndType(facemesh.name, 'MESH')
        facemesh_world_matrix = facemesh_obj.matrix_world
        for bone_name in facemesh_config_data['bone_positions'].keys():
            if bone_name.lower() == 'desc':
                continue
            bone_id = armature.bones.find(bone_name)
            # print('%s = %s' % (bone_name, bone_id))
            head = facemesh_config_data['bone_positions'][bone_name]['head']
            if head is not None:
                facemesh_co = facemesh.vertices[head].co
                world_co = facemesh_world_matrix @ facemesh_co
                # bpy.data.objects[armature.name].data.edit_bones[bone_id].head = facemesh_co
                armature_obj.data.edit_bones[bone_id].head = armature_world_matrix_inverted @ world_co
            
            tail = facemesh_config_data['bone_positions'][bone_name]['tail']
            if tail is not None:
                facemesh_co = facemesh.vertices[tail].co
                world_co = facemesh_world_matrix @ facemesh_co
                # bpy.data.objects[armature.name].data.edit_bones[bone_id].tail = facemesh_co
                armature_obj.data.edit_bones[bone_id].tail = armature_world_matrix_inverted @ world_co

        eye_bone_names = []
        eye_objs = []
        missing_eyes = []
        if context.scene.cyanic_eye_left is not None:
            eye_bone_names.append('eye.L')
            eye_objs.append(findObjectByNameAndType(context.scene.cyanic_eye_left.name, 'MESH'))
        else:
            missing_eyes.append('eye.L')

        if context.scene.cyanic_eye_right is not None:
            eye_bone_names.append('eye.R')
            eye_objs.append(findObjectByNameAndType(context.scene.cyanic_eye_right.name, 'MESH'))
        else:
            missing_eyes.append('eye.R')

        # if context.scene.cyanic_eye_left is not None and context.scene.cyanic_eye_right is not None:
        if len(eye_objs) > 0:
            # Position the eyes
            # eye_bone_names = ['eye.L', 'eye.R']
            # eye_objs = [findObjectByNameAndType(context.scene.cyanic_eye_left.name, 'MESH'), findObjectByNameAndType(context.scene.cyanic_eye_right.name, 'MESH')]
            for index in range(len(eye_objs)):
                bone_id = armature.bones.find(eye_bone_names[index])
                bone_head_location = armature_obj.data.edit_bones[bone_id].head
                bone_head_new_location = armature_world_matrix_inverted @ eye_objs[index].location # World location of origin
                bone_translation = bone_head_location - bone_head_new_location
                bone_tail_new_location = armature_obj.data.edit_bones[bone_id].tail - bone_translation
                armature_obj.data.edit_bones[bone_id].head = bone_head_new_location
                armature_obj.data.edit_bones[bone_id].tail = bone_tail_new_location

        if len(missing_eyes) > 0:
            # TODO: Position between eye holes
            for index in range(len(missing_eyes)):
                bone_id = armature.bones.find(missing_eyes[index])
                # Find world location of the point between
                # bone length should be equal to width of eye

        bpy.ops.object.mode_set(mode=starting_mode)
        return {'FINISHED'}



# IIRC Eyes are particularly annoying to parent
class ParentFacemeshToRigOperator(bpy.types.Operator):
    bl_idname = "object.parentfacemeshtorig"
    bl_label = "ParentFacemeshToRig"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        return {'FINISHED'}
