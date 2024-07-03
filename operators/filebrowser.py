import bpy

class FileBrowserOperator(bpy.types.Operator):
    """Select image to convert into a face mesh"""
    bl_idname = "open.filebrowser"
    bl_label = "FileBrowser"

    # filepath = bpy.props.StringProperty(subtype="FILE_PATH") 
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.cyanic_img_path = self.filepath

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        #Open browser, take reference to 'self' 
        #read the path to selected file, 
        #put path in declared string type data structure self.filepath

        return {'RUNNING_MODAL'}  
        # Tells Blender to hang on for the slow user input
