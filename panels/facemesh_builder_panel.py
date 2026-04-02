import bpy

from ..operators import FileBrowserOperator, FaceImg2FacemeshOperator, FacemeshDefaultOperator

class FACEMESH_BUILDER_PT_Panel(bpy.types.Panel):
    bl_label = "Create Facemesh"
    bl_idname = "FACEMESH_BUILDER_PT_Panel"
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

        sub.prop(view, 'cyanic_img_path')
        # col.operator(FileBrowserOperator.bl_idname, text='Select face image')
        # Preview face image?
        # image = bpy.data.images['']
        # icon_id = bpy.types.UILayout.icon(image)
        # layout.template_icon(icon_value=icon_id)

        # col.enabled = context.scene.cyanic_img_path != None and len(context.scene.cyanic_img_path) > 0
        col.operator(FaceImg2FacemeshOperator.bl_idname, text='Create Facemesh')

        col2 = layout.column(align=True)
        col2.operator(FacemeshDefaultOperator.bl_idname, text='Add Empty Facemesh')