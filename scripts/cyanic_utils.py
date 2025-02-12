import bpy
import os
import json

# from mathutils import *
# D = bpy.data
# C = bpy.context

class CyanicUtils():
    def __init__(self):
        self.facemesh_config_data = {}

    def init_variables(self):
        self.script_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(os.path.split(self.script_dir)[0], 'data')
        self.facemesh_mapping_file = os.path.join(self.data_dir, 'facemesh_rigify_mapping.json')
        self.facemesh_config_data = {}

    def load_config(self):
        try:
            self.script_dir
        except:
            self.init_variables()
        
        # with open(os.path.join(root_url, facemesh_mapping_file), 'r') as input_file:
        with open(self.facemesh_mapping_file, 'r') as input_file:
            string_format = input_file.read()
            self.facemesh_config_data = json.loads(string_format)

    def get_facemesh_config_data(self):
        if len(self.facemesh_config_data.keys()) == 0:
            self.load_config()
        return self.facemesh_config_data

    def findObjectByNameAndType(self, name, obj_type):
        objects = [obj for obj in bpy.context.scene.objects if obj.type == obj_type and obj.data.name == name]
        if len(objects) == 1:
            return objects[0]
        # print('Found %s objects for %s, %s' % (len(objects), name, obj_type))
        # print(objects)
        return objects[-1]

    def selectObject(self, name, obj_type, clear_old=True):
        if clear_old:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
            except:
                pass # If there's no object selected, it can't do either option
        obj = self.findObjectByNameAndType(name, obj_type)
        bpy.context.view_layer.objects.active = obj # Active object is what transform_apply is interacting with
        bpy.data.objects[obj.name].select_set(True)
        return obj
