import bpy

from ..operators import FileBrowserOperator, FaceImg2FacemeshOperator

class FACEMESH_BUILDER_PT_Panel(bpy.types.Panel):
    bl_label = "Facemesh Builder"
    bl_idname = "FACEMESH_BUILDER_PT_Panel"
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
        
        sub.prop(view, 'cyanic_img_path')
        # col.operator(FileBrowserOperator.bl_idname, text='Select face image')
        # Preview face image?
        col.operator(FaceImg2FacemeshOperator.bl_idname, text='Create face mesh')
