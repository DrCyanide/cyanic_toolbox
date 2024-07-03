import bpy

from ..operators import GenRigFromMetaRigOperator, MocapOperator

class MOCAP_PT_Panel(bpy.types.Panel):
    bl_label = "Mocap"
    bl_idname = "MOCAP_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'object'
    bl_category = 'Cyanic'

    def draw(self, context):
        layout = self.layout

        # layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # view = context.space_data
        view = context.scene

        col = layout.column(align=True)
        sub = col.column()
        
        sub.prop(view, 'cyanic_rigify_gen_rig')

        col.operator(GenRigFromMetaRigOperator.bl_idname, text='Select Rig from Meta-rig')

        # Image / Video
        row1 = layout.row()
        row1.prop(view, 'cyanic_source_type', expand=True)
        # File / Webcam
        row2 = layout.row()
        row2.prop(view, 'cyanic_source_input', expand=True)

        # File Source
        row3 = layout.row()
        row3.prop(view, 'cyanic_mocap_file_path')

        # If webcam, need option to record, with timer delay
        col2 = layout.column(align=True)
        col2.operator(MocapOperator.bl_idname, text='Generate mocap')
