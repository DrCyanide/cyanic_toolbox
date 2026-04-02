import bpy
import mathutils
from ..scripts import CyanicUtils

hand_config_data = {}
cu = CyanicUtils()

def init_config():
    global hand_config_data
    if len(hand_config_data.keys()) == 0:
        hand_config_data = cu.get_hand_config_data()


class RigHandsOperator(bpy.types.Operator):
    """Align the Rigify hand bones to the prefab hands"""
    bl_idname = "object.cyanic_rig_hands"
    bl_label = "Rig Hands"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for operations

    def execute(self, context):
        if len(hand_config_data.keys()) == 0:
            # load_config()
            init_config()

        starting_mode = 'OBJECT'
        try:
            starting_mode = bpy.context.object.mode
        except:
            pass # No object selected, likely in object mode already

        self.armature_obj = self.get_armature_obj()
        self.handle_hand(context.scene.cyanic_hand_left, side='L')
        self.handle_hand(context.scene.cyanic_hand_right, side='R')

        bpy.ops.object.mode_set(mode=starting_mode)

        return {'FINISHED'}

    def get_armature_obj(self):
        # Get the metarig
        armature = bpy.context.scene.cyanic_rigify_metarig
        if armature is None:
            # Add Rig
            bpy.ops.object.armature_human_metarig_add()
            scene_armatures = bpy.data.armatures
            bpy.context.scene.cyanic_rigify_metarig = scene_armatures[-1]
            armature = bpy.context.scene.cyanic_rigify_metarig

        armature_obj = cu.findObjectFromOther(armature)
        return armature_obj
    
    def average_verts_location(self, hand, verts_list):
        selected_verts = list(filter(lambda v: v.index in verts_list, hand.vertices))
        vert_count = len(selected_verts)
        avg_x = sum(list(map(lambda v: v.co.x, selected_verts))) / vert_count
        avg_y = sum(list(map(lambda v: v.co.y, selected_verts))) / vert_count
        avg_z = sum(list(map(lambda v: v.co.z, selected_verts))) / vert_count
        
        return mathutils.Vector((avg_x, avg_y, avg_z))

    def handle_hand(self, hand, side='R'):
        if hand == None:
            # This hand isn't assigned, so don't mess with it.
            return
        cu.deselectAll()
        cu.selectObject(self.armature_obj)
        bpy.ops.object.mode_set(mode='EDIT')

        finger_mapping = {
            'thumb': 'thumb',
            'index': 'f_index',
            'middle': 'f_middle',
            'ring': 'f_ring',
            'pinky': 'f_pinky'
        }
        palm_mapping = {
            'index': '01',
            'middle': '02',
            'ring': '03',
            'pinky': '04'
        }

        hand_verts = len(hand.vertices)
        hand_obj = cu.findObjectFromOther(hand)
        hand_world_matrix = hand_obj.matrix_world
        armature_world_matrix_inverted = self.armature_obj.matrix_world.inverted()
        for hand_style in hand_config_data['prefabs']:
            # Determine which hand config to use by matching vert counts. If the user deletes verts this won't match.
            # A separate config would need to be made for common edits (like deleting the wrist stub faces to allow shrink wrapping)
            if hand_config_data['prefabs'][hand_style]["total_verts"] == hand_verts:
                hand_config = hand_config_data['prefabs'][hand_style]
                # Wrist
                wrist_world_co = hand_world_matrix @ self.average_verts_location(hand, hand_config['wrist']['hand_bone_base'])
                self.armature_obj.data.edit_bones['hand.%s' % side].head = armature_world_matrix_inverted @ wrist_world_co
                # Palm
                palm_world_co = hand_world_matrix @ self.average_verts_location(hand, hand_config['wrist']['hand_bone_tip'])
                self.armature_obj.data.edit_bones['hand.%s' % side].tail = armature_world_matrix_inverted @ palm_world_co

                for digit_name in finger_mapping.keys():
                    # Tip
                    tip_co = hand_world_matrix @ self.average_verts_location(hand, hand_config[digit_name]['tip'])
                    self.armature_obj.data.edit_bones['%s.03.%s' % (finger_mapping[digit_name], side)].tail = armature_world_matrix_inverted @ tip_co
                    # Knuckle_1
                    knuckle_1_co = hand_world_matrix @ self.average_verts_location(hand, hand_config[digit_name]['knuckle_1'])
                    self.armature_obj.data.edit_bones['%s.02.%s' % (finger_mapping[digit_name], side)].tail = armature_world_matrix_inverted @ knuckle_1_co
                    self.armature_obj.data.edit_bones['%s.03.%s' % (finger_mapping[digit_name], side)].head = armature_world_matrix_inverted @ knuckle_1_co
                    # Knuckle_2
                    knuckle_2_co = hand_world_matrix @ self.average_verts_location(hand, hand_config[digit_name]['knuckle_2'])
                    self.armature_obj.data.edit_bones['%s.01.%s' % (finger_mapping[digit_name], side)].tail = armature_world_matrix_inverted @ knuckle_2_co
                    self.armature_obj.data.edit_bones['%s.02.%s' % (finger_mapping[digit_name], side)].head = armature_world_matrix_inverted @ knuckle_2_co
                    # Knuckle_3
                    knuckle_3_co = hand_world_matrix @ self.average_verts_location(hand, hand_config[digit_name]['knuckle_3'])
                    self.armature_obj.data.edit_bones['%s.01.%s' % (finger_mapping[digit_name], side)].head = armature_world_matrix_inverted @ knuckle_3_co
                    # Palm
                    if digit_name != 'thumb':
                        self.armature_obj.data.edit_bones['palm.%s.%s' % (palm_mapping[digit_name], side)].tail = armature_world_matrix_inverted @ knuckle_3_co
                        palm_co = hand_world_matrix @ self.average_verts_location(hand, hand_config[digit_name]['palm'])
                        self.armature_obj.data.edit_bones['palm.%s.%s' % (palm_mapping[digit_name], side)].head = armature_world_matrix_inverted @ palm_co
                    