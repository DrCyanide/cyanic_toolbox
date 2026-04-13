import bpy

class MESHES_GENERAL_PT_Panel(bpy.types.Panel):
    bl_label = 'Meshes'
    bl_idname = 'MESHES_GENERAL_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cyanic'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False  # No animation.

        # col = self.layout.column(align=True)
        # sub = col.column()
        
        # sub.prop(context.scene, 'cyanic_facemesh')


class MESHES_FACE_PT_Panel(bpy.types.Panel):
    bl_label = 'Face'
    bl_idname = 'MESHES_FACE_PT_Panel'
    bl_parent_id = 'MESHES_GENERAL_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    b_category = 'Cyanic'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False # No animation.
        

        col = self.layout.column(align=True)
        sub = col.column()

        sub.prop(context.scene, 'cyanic_facemesh')

        sub1 = col.column()
        sub1.prop(context.scene, 'cyanic_eye_left')
        
        sub2 = col.column()
        sub2.prop(context.scene, 'cyanic_eye_right')
        
        sub3 = col.column()
        sub3.prop(context.scene, 'cyanic_mouth_top')
               
        sub4 = col.column()
        sub4.prop(context.scene, 'cyanic_mouth_bottom')
        
        sub5 = col.column()
        sub5.prop(context.scene, 'cyanic_mouth_tongue')

class MESHES_HANDS_PT_Panel(bpy.types.Panel):
    bl_label = 'Hands'
    bl_idname = 'MESHES_HANDS_PT_Panel'
    bl_parent_id = 'MESHES_GENERAL_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cyanic'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False # No animation

        col = self.layout.column(align=True)

        sub1 = col.column()
        sub1.prop(context.scene, 'cyanic_hand_left')

        sub2 = col.column()
        sub2.prop(context.scene, 'cyanic_hand_right')
