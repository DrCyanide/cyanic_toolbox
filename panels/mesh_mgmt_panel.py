import bpy
from ..operators import MoveEyesToSocketsOperator

class MESH_MANAGEMENT_PT_Panel(bpy.types.Panel):
    bl_label = 'Mesh Management'
    bl_idname = 'MESH_MANAGEMENT_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cyanic'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False # No animation.

        col = self.layout.column(align=True)

        move_eyes_col = col.column()
        move_eyes_col.operator(MoveEyesToSocketsOperator.bl_idname, text='Eyes to Sockets')
        move_eyes_col.enabled = context.scene.cyanic_eye_left != None or context.scene.cyanic_eye_right != None


# NOTE: Move all the Facemesh Generation, Facemesh Cleanup, and Eye Alignment options here