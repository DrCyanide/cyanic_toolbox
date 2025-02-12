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

class MoveEyesToSockets(bpy.types.Operator):
    """Move the eyes to the center of the sockets"""
    bl_idname = "object.cyanic_eyeposition"
    bl_label = "Cyanic_EYE_POSITION"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        init_config()
        facemesh = context.scene.cyanic_facemesh
        if facemesh is None:
            return {'CANCELLED'}

        starting_mode = 'OBJECT'
        try:
            starting_mode = bpy.context.object.mode
        except:
            pass # No object selected, likely in object mode already

        if context.scene.cyanic_eye_left is not None:
            # Find global positions of the facemesh verts
            eye_socket_data = facemesh_config_data['midpoint_verts']['eye.L']
            world_co_target = self.calculate_position(context, eye_socket_data)
            # Set the world coords of cyanic_eye_left
            bpy.ops.object.mode_set(mode='OBJECT')
            eye_obj = cu.selectObject(context.scene.cyanic_eye_left.name, 'MESH')
            eye_obj.location = world_co_target

        if context.scene.cyanic_eye_right is not None:
            eye_socket_data = facemesh_config_data['midpoint_verts']['eye.R']
            world_co_target = self.calculate_position(context, eye_socket_data)
            # Set the world coords of cyanic_eye_left
            bpy.ops.object.mode_set(mode='OBJECT')
            eye_obj = cu.selectObject(context.scene.cyanic_eye_right.name, 'MESH')
            eye_obj.location = world_co_target

        bpy.ops.object.mode_set(mode=starting_mode)
        return {'FINISHED'}

    def calculate_position(self, context, eye_socket_data):
        facemesh = context.scene.cyanic_facemesh
        facemesh_obj = cu.findObjectByNameAndType(facemesh.name, 'MESH')
        facemesh_world_matrix = facemesh_obj.matrix_world
        # X and Y
        facemesh_co_h0 = facemesh.vertices[eye_socket_data['horizontal'][0]].co
        facemesh_co_h1 = facemesh.vertices[eye_socket_data['horizontal'][1]].co
        world_co_h0 = facemesh_world_matrix @ facemesh_co_h0
        world_co_h1 = facemesh_world_matrix @ facemesh_co_h1
        world_co_h_mid = (world_co_h0 + world_co_h1) / 2

        # Z
        facemesh_co_v0 = facemesh.vertices[eye_socket_data['vertical'][0]].co
        facemesh_co_v1 = facemesh.vertices[eye_socket_data['vertical'][1]].co
        world_co_v0 = facemesh_world_matrix @ facemesh_co_v0
        world_co_v1 = facemesh_world_matrix @ facemesh_co_v1
        world_co_v_mid = (world_co_v0 + world_co_v1) / 2

        world_co_target = world_co_h_mid
        world_co_target.z = world_co_v_mid.z
        return world_co_target


class ParentEyesToRig(bpy.types.Operator):
    """Parent the eyes to the bones of the rig"""
    bl_idname = "object.cyanic_eyeparent"
    bl_label = "Cyanic_EYE_PARENT"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # init_config()
        if context.scene.cyanic_rigify_gen_rig is None:
            return {'CANCELLED'}
        
        starting_mode = 'OBJECT'
        try:
            starting_mode = bpy.context.object.mode
        except:
            pass # No object selected, likely in object mode already

        self.clear_selected_objs()
        self.clear_selected_bones()
        self.parent_eye(context, context.scene.cyanic_eye_right, 'R')

        self.clear_selected_objs()
        self.clear_selected_bones()
        self.parent_eye(context, context.scene.cyanic_eye_left, 'L')

        self.clear_selected_objs()
        self.clear_selected_bones()

        bpy.ops.object.mode_set(mode=starting_mode)
        return {'FINISHED'}

    def clear_selected_bones(self):
        armature_obj = cu.selectObject(bpy.context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
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

    def clear_selected_objs(self):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass # If there's no object selected, it can't do either option

    def parent_eye(self, context, eye, side_initial='L'):
        if eye is not None:
            # Select eye
            eye_obj = cu.selectObject(eye.name, 'MESH')
            # Select armature
            armature_obj = cu.selectObject(context.scene.cyanic_rigify_gen_rig.name, 'ARMATURE', clear_old=False)
            # Set mode to POSE
            bpy.ops.object.mode_set(mode='POSE')
            starting_MCH_status = bpy.context.object.data.collections_all['MCH'].is_visible
            bpy.context.object.data.collections_all['MCH'].is_visible = True

            # Select the bone
            # ... This has been a pain, so yes, I'm throwing everything at it trying to get ANYTHING to work
            # I *think* .select sets it as selected in the viewport
            bpy.context.object.data.bones.active = bpy.data.objects[armature_obj.name].data.bones['MCH-eye.' + side_initial] # This is what actually ends up selecting the bone...
            bpy.data.objects[armature_obj.name].pose.bones['MCH-eye.' + side_initial].bone.select = True
            bpy.data.objects[armature_obj.name].data.bones['MCH-eye.' + side_initial].select = True
            context.scene.cyanic_rigify_gen_rig.bones['MCH-eye.' + side_initial].select = True

            # Parent
            bpy.ops.object.parent_set(type='BONE')
            bpy.context.object.data.collections_all['MCH'].is_visible = starting_MCH_status

            # Reset the bone to deselected
            bpy.data.objects[armature_obj.name].pose.bones['MCH-eye.' + side_initial].bone.select = False
            bpy.data.objects[armature_obj.name].data.bones['MCH-eye.' + side_initial].select = False
            context.scene.cyanic_rigify_gen_rig.bones['MCH-eye.' + side_initial].select = False
