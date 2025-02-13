import bpy

from ..operators import MoveEyesToSocketsOperator, ParentEyesToRigOperator

class EYE_MGMT_PT_Panel(bpy.types.Panel):
    bl_label = "Eye Management"
    bl_idname = "EYE_MGMT_PT_Panel"
    bl_parent_id = "FACEMESH_GENERAL_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'object'
    bl_category = 'Cyanic'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # view = context.space_data
        view = context.scene

        col = layout.column(align=True)
        sub = col.column()
        
        sub.prop(view, 'cyanic_eye_left')
        sub.prop(view, 'cyanic_eye_right')

        move_eyes_col = sub.column()
        move_eyes_col.operator(MoveEyesToSocketsOperator.bl_idname, text='Eyes to Sockets')

        parent_rig_col = sub.column()
        parent_rig_col.operator(ParentEyesToRigOperator.bl_idname, text='Parent Eyes to Rig')
        parent_rig_col.enabled = context.scene.cyanic_rigify_gen_rig != None and (context.scene.cyanic_eye_left != None or context.scene.cyanic_eye_right != None)


        # rig_col = sub.column()
        # rig_col.operator(RigFacemeshOperator.bl_idname, text='Rig face + eyes')
        # rig_col.enabled = context.scene.cyanic_rigify_metarig != None and  context.scene.cyanic_facemesh != None

        # Convert Meta-rig to Rig
        # col.operator("pose.rigify_generate", text='Active Metarig to Rig') # https://github.com/eigen-value/rigify/blob/ed06fe9461f537c329d471fd7f3b9babcff2366e/ui.py#L96
        # sub.prop(view, 'cyanic_rigify_gen_rig')
        # convert_col = sub.column()
        # convert_col.operator(GenRigFromMetaRigOperator.bl_idname, text='Metarig to Rig')
        # convert_col.enabled = context.scene.cyanic_rigify_metarig != None and context.scene.cyanic_rigify_gen_rig == None

        # Parent objects to Rig