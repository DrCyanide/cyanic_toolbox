import bpy
import os

class FacemeshDefaultOperator(bpy.types.Operator):
    """Import the default facemesh, without texture"""
    bl_idname = "object.facemesh_default"
    bl_label = "FacemeshDefault"

    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.split(script_dir)[0], 'data')

    def execute(self, context):
        bpy.ops.wm.obj_import(filepath=os.path.join(self.data_dir, 'canonical_face_model.obj'))
        # The object is now the active object, assign it to cyanic_facemesh
        context.scene.cyanic_facemesh = bpy.context.view_layer.objects.active.data # Gets the active mesh (data) instead of just the object
        return {'FINISHED'}

    