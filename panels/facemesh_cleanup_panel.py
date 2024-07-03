import bpy

from ..operators import FacemeshCleanupSymmetrizeOperator, FacemeshCleanupOpenMouthOperator, FacemeshCleanupOpenEyesOperator, FacemeshCleanupCloseEyesOperator, FacemeshCleanupCloseMouthOperator

class FACEMESH_CLEANUP_PT_Panel(bpy.types.Panel):
    bl_label = "Cleanup"
    bl_idname = "FACEMESH_CLEANUP_PT_Panel"
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
        
        # layout.label(text="Snap to Symmetry might make mistakes. If so, manually edit verts to be closer to symmetrical then try again.")
        col.operator(FacemeshCleanupSymmetrizeOperator.bl_idname, text='Snap to Symmetry')
        col.operator(FacemeshCleanupOpenEyesOperator.bl_idname, text='Open eyes')
        col.operator(FacemeshCleanupOpenMouthOperator.bl_idname, text='Open mouth')
        
        col.operator(FacemeshCleanupCloseEyesOperator.bl_idname, text='Close eyes')
        col.operator(FacemeshCleanupCloseMouthOperator.bl_idname, text='Close mouth')

