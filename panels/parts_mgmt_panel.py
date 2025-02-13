import bpy

class PARTS_MGMT_PT_Panel(bpy.types.Panel):
    bl_label = "Facial parts"
    bl_idname = "PARTS_MGMT_PT_Panel"
    # bl_parent_id = "FACEMESH_GENERAL_PT_Panel"
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
        sub.prop(view, 'cyanic_mouth_top')
        sub.prop(view, 'cyanic_mouth_bottom')
        sub.prop(view, 'cyanic_mouth_tongue')