import bpy

from ..operators import GenRigFromMetaRigOperator, ParentFacemeshToRigOperator, ParentEyesToRigOperator, ParentMouthToRigOperator

class RIGGING_PT_Panel(bpy.types.Panel):
    bl_label = "Rigging"
    bl_idname = "RIGGING_PT_Panel"
    bl_parent_id = "RIGGING_MGMT_PT_Panel"
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

        # Convert Meta-rig to Rig
        # col.operator("pose.rigify_generate", text='Active Metarig to Rig') # https://github.com/eigen-value/rigify/blob/ed06fe9461f537c329d471fd7f3b9babcff2366e/ui.py#L96
        sub.prop(view, 'cyanic_rigify_gen_rig')
        convert_col = sub.column()
        convert_col.operator(GenRigFromMetaRigOperator.bl_idname, text='Metarig to Rig')
        convert_col.enabled = context.scene.cyanic_rigify_metarig != None and context.scene.cyanic_rigify_gen_rig == None

        # Parent facemesh to Rig
        parent_facemesh_col = sub.column()
        parent_facemesh_col.operator(ParentFacemeshToRigOperator.bl_idname, text='Parent Facemesh to Rig')
        parent_facemesh_col.enabled = context.scene.cyanic_rigify_gen_rig != None and context.scene.cyanic_facemesh != None

        # Parent eyes to Rig
        parent_eyes_col = sub.column()
        parent_eyes_col.operator(ParentEyesToRigOperator.bl_idname, text='Parent Eyes to Rig')
        parent_eyes_col.enabled = context.scene.cyanic_rigify_gen_rig != None and (context.scene.cyanic_eye_left != None or context.scene.cyanic_eye_right != None)

        # Parent mouth to Rig
        parent_mouth_col = sub.column()
        parent_mouth_col.operator(ParentMouthToRigOperator.bl_idname, text='Parent Mouth to Rig')
        parent_mouth_col.enabled = context.scene.cyanic_rigify_gen_rig != None and (context.scene.cyanic_mouth_top != None or context.scene.cyanic_mouth_bottom != None or context.scene.cyanic_mouth_tongue != None)

