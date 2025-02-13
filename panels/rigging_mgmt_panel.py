import bpy

class RIGGING_MGMT_PT_Panel(bpy.types.Panel):
    bl_label = "Rigging"
    bl_idname = "RIGGING_MGMT_PT_Panel"
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