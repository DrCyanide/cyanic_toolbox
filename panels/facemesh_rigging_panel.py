import bpy

from ..operators import RigFacemeshOperator, ParentFacemeshToRigOperator, AddRigOperator

class FACEMESH_RIGGING_PT_Panel(bpy.types.Panel):
    bl_label = "Rig"
    bl_idname = "FACEMESH_RIGGING_PT_Panel"
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
        sub.prop(view, 'cyanic_rigify_rig')

        col.operator(AddRigOperator.bl_idname, text='Create Meta-rig')
        col.operator(RigFacemeshOperator.bl_idname, text='Rig face + eyes')
        # Convert Meta-rig to Rig
        # Parent objects to Rig