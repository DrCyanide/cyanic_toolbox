import bpy

from ..operators import RigFacemeshOperator, AddRigOperator, MoveEyesToSocketsOperator

class METARIGGING_PT_Panel(bpy.types.Panel):
    bl_label = "Meta-rigging"
    bl_idname = "METARIGGING_PT_Panel"
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
        
        sub.prop(view, 'cyanic_rigify_metarig')

        metarig_col = sub.column()
        metarig_col.operator(AddRigOperator.bl_idname, text='Create Metarig')
        metarig_col.enabled = context.scene.cyanic_rigify_metarig == None

        move_eyes_col = sub.column()
        move_eyes_col.operator(MoveEyesToSocketsOperator.bl_idname, text='Eyes to Sockets')
        move_eyes_col.enabled = context.scene.cyanic_eye_left != None or context.scene.cyanic_eye_right != None

        rig_col = sub.column()
        rig_col.operator(RigFacemeshOperator.bl_idname, text='Align Metarig')
        rig_col.enabled = context.scene.cyanic_rigify_metarig != None and  context.scene.cyanic_facemesh != None
