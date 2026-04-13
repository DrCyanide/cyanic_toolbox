import bpy
import os
import json
from ..scripts import CyanicUtils

facemesh_config_data = {}
cu = CyanicUtils()

def init_config():
    global facemesh_config_data
    if len(facemesh_config_data.keys()) == 0:
        facemesh_config_data = cu.get_facemesh_config_data()


class AddRigOperator(bpy.types.Operator):
    """Add a Rigify Meta-Rig to the scene"""
    bl_idname = "object.cyanic_add_rig"
    bl_label = "Add Metarig"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        # Add Rig
        bpy.ops.object.armature_human_metarig_add()
        scene_armatures = bpy.data.armatures
        context.scene.cyanic_rigify_metarig = scene_armatures[-1]
        # armature = context.scene.cyanic_rigify_metarig
        return {'FINISHED'}


class RigFacemeshOperator(bpy.types.Operator):
    """Align the Rigify face bones to the facemesh. If eyes are selected, their bones will be lined up too"""
    bl_idname = "object.cyanic_rig_facemesh"
    bl_label = "Rig Facemesh"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if len(facemesh_config_data.keys()) == 0:
            # load_config()
            init_config()
        
        facemesh = context.scene.cyanic_facemesh
        armature = context.scene.cyanic_rigify_metarig
        
        if armature is None:
            # Add Rig
            bpy.ops.object.armature_human_metarig_add()
            scene_armatures = bpy.data.armatures
            context.scene.cyanic_rigify_metarig = scene_armatures[-1]
            armature = context.scene.cyanic_rigify_metarig

        starting_mode = 'OBJECT'
        try:
            starting_mode = bpy.context.object.mode
        except:
            pass # No object selected, likely in object mode already

        # armature_obj = cu.selectObjectByName(armature.name, 'ARMATURE')
        armature_obj = cu.selectObject(armature)
        armature_world_matrix_inverted = armature_obj.matrix_world.inverted()
        bpy.ops.object.mode_set(mode='EDIT')

        # facemesh_obj = cu.findObjectByNameAndType(facemesh.name, 'MESH')
        facemesh_obj = cu.findObjectFromOther(facemesh)
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
            # eye_objs.append(cu.findObjectByNameAndType(context.scene.cyanic_eye_left.name, 'MESH'))
            eye_objs.append(cu.findObjectFromOther(context.scene.cyanic_eye_left))
        else:
            missing_eyes.append('eye.L')

        if context.scene.cyanic_eye_right is not None:
            eye_bone_names.append('eye.R')
            # eye_objs.append(cu.findObjectByNameAndType(context.scene.cyanic_eye_right.name, 'MESH'))
            eye_objs.append(cu.findObjectFromOther(context.scene.cyanic_eye_right))
        else:
            missing_eyes.append('eye.R')

        # if context.scene.cyanic_eye_left is not None and context.scene.cyanic_eye_right is not None:
        if len(eye_objs) > 0:
            # Position the eyes
            # eye_bone_names = ['eye.L', 'eye.R']
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

        try:
            bpy.ops.object.mode_set(mode=starting_mode)
        except:
            pass
        return {'FINISHED'}


class GenRigFromMetaRigOperator(bpy.types.Operator):
    """Convert metarig to rig"""
    bl_idname = "object.cyanic_gen_rig_from_metarig"
    bl_label = "Generate Rig from Metarig"

    def execute(self, context):
        if context.scene.cyanic_rigify_metarig is None:
            self.report({'ERROR_INVALID_INPUT'}, 'No Rigify metarig selected')
            return {'CANCELLED'}

        # Get a set of all objects
        initial_objects = set(bpy.context.scene.objects)

        # Select the metarig so that rigify can modify it
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass # If there's no object selected, it can't do either option
        for obj in bpy.context.scene.objects:
            if obj.data == context.scene.cyanic_rigify_metarig:
                bpy.context.view_layer.objects.active = obj
                bpy.data.objects[obj.name].select_set(True)
                break
        
        # Convert the metarig
        bpy.ops.pose.rigify_generate()

        # Get an updated set of all objects (new one is the rig)
        final_objects = set(bpy.context.scene.objects)

        # Update context.scene.cyanic_rigify_gen_rig
        new_object = final_objects - initial_objects
        if len(new_object) > 0:
            context.scene.cyanic_rigify_gen_rig = new_object.pop().data

        return {'FINISHED'}


# Eyes are handled in eye_tools
class ParentFacemeshToRigOperator(bpy.types.Operator):
    bl_idname = "object.cyanic_parent_facemesh_to_rig"
    bl_label = "Parent Facemesh to Rig"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if context.scene.cyanic_rigify_gen_rig is None:
            self.report({'ERROR_INVALID_INPUT'}, 'No Rigify rig selected')
            return {'CANCELLED'}
        if context.scene.cyanic_facemesh is None:
            self.report({'ERROR_INVALID_INPUT'}, 'No facemesh selected')
            return {'CANCELLED'}
        
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass # If there's no object selected, it can't do either option

        # Select Facemesh
        # facemesh_obj = cu.selectObjectByName(context.scene.cyanic_facemesh.name, 'MESH')
        facemesh_obj = cu.selectObject(context.scene.cyanic_facemesh)

        # Select Rig
        # armature_obj = cu.selectObjectByName(context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
        armature_obj = cu.selectObject(context.scene.cyanic_rigify_gen_rig, clear_old=False)

        # Parent it
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        return {'FINISHED'}

class ParentMouthToRigOperator(bpy.types.Operator):
    bl_idname = "object.cyanic_parent_mouth_to_rig"
    bl_label = "Parent Mouth to Rig"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def clear_selected_objs(self):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass # If there's no object selected, it can't do either option

    def clear_selected_bones(self):
        # armature_obj = cu.selectObjectByName(bpy.context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
        armature_obj = cu.selectObject(bpy.context.scene.cyanic_rigify_gen_rig, clear_old=False)
        for bone in bpy.data.objects[armature_obj.name].data.bones:
            bpy.data.objects[armature_obj.name].pose.bones[bone.name].bone.select = False
            bpy.data.objects[armature_obj.name].data.bones[bone.name].select = False
            bpy.context.scene.cyanic_rigify_gen_rig.bones[bone.name].select = False
        try:
            last_mode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='POSE')
            bpy.context.active_pose_bone.bone.select = False
            bpy.ops.object.mode_set(mode=last_mode)
        except:
            pass

    def execute(self, context):
        if context.scene.cyanic_rigify_gen_rig is None:
            self.report({'ERROR_INVALID_INPUT'}, 'No Rigify rig selected')
            return {'CANCELLED'}

        starting_ORG_status = bpy.context.object.data.collections_all['ORG'].is_visible
        bpy.context.object.data.collections_all['ORG'].is_visible = True

        if context.scene.cyanic_mouth_top != None:
            self.clear_selected_objs()
            self.clear_selected_bones()
            # mouth_obj = cu.selectObjectByName(context.scene.cyanic_mouth_top.name, 'MESH')
            mouth_obj = cu.selectObject(context.scene.cyanic_mouth_top)
            # Select Rig
            # armature_obj = cu.selectObjectByName(context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
            armature_obj = cu.selectObject(context.scene.cyanic_rigify_gen_rig, clear_old=False)
            # Select the bones inside the rig
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.context.object.data.bones.active = bpy.data.objects[armature_obj.name].data.bones['ORG-teeth.T']
            bpy.data.objects[armature_obj.name].pose.bones['ORG-teeth.T'].bone.select = True
            bpy.data.objects[armature_obj.name].data.bones['ORG-teeth.T'].select = True
            # Parent it
            bpy.ops.object.parent_set(type='BONE')
            
        if context.scene.cyanic_mouth_bottom != None:
            self.clear_selected_objs()
            self.clear_selected_bones()
            # mouth_obj = cu.selectObjectByName(context.scene.cyanic_mouth_bottom.name, 'MESH')
            mouth_obj = cu.selectObject(context.scene.cyanic_mouth_bottom)
            # Select Rig
            # armature_obj = cu.selectObjectByName(context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
            armature_obj = cu.selectObject(context.scene.cyanic_rigify_gen_rig, clear_old=False)
            # Select the bones inside the rig
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.context.object.data.bones.active = bpy.data.objects[armature_obj.name].data.bones['ORG-teeth.B']
            bpy.data.objects[armature_obj.name].pose.bones['ORG-teeth.B'].bone.select = True
            bpy.data.objects[armature_obj.name].data.bones['ORG-teeth.B'].select = True
            # Parent it
            bpy.ops.object.parent_set(type='BONE')

        if context.scene.cyanic_mouth_tongue != None:
            self.clear_selected_objs()
            self.clear_selected_bones()
            # mouth_obj = cu.selectObjectByName(context.scene.cyanic_mouth_tongue.name, 'MESH')
            mouth_obj = cu.selectObject(context.scene.cyanic_mouth_tongue)
            # Select Rig
            # armature_obj = cu.selectObjectByName(context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
            armature_obj = cu.selectObject(context.scene.cyanic_rigify_gen_rig, clear_old=False)
            # Select the bones inside the rig
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            bone_names = ['DEF-tongue', 'DEF-tongue.001', 'DEF-tongue.002']
            for bone_name in bone_names:
                # Not selecting right...
                bpy.context.object.data.bones.active = bpy.data.objects[armature_obj.name].data.bones[bone_name]
                bpy.data.objects[armature_obj.name].pose.bones[bone_name].bone.select = True
                bpy.data.objects[armature_obj.name].data.bones[bone_name].select = True
            # Parent it 
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        bpy.context.object.data.collections_all['ORG'].is_visible = starting_ORG_status

        return {'FINISHED'}
        bpy.data.objects[armature_obj.name].data.bones[bone_name]
