import bpy
import os
import json

# from mathutils import *
# D = bpy.data
# C = bpy.context

class CyanicUtils():
    def __init__(self):
        self.facemesh_config_data = {}
        self.hand_config_data = {}

    def init_variables(self):
        self.script_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(os.path.split(self.script_dir)[0], 'data')
        self.facemesh_mapping_file = os.path.join(self.data_dir, 'facemesh_rigify_mapping.json')
        self.hand_mapping_file = os.path.join(self.data_dir, 'hands_rigify_mapping.json')
        self.facemesh_config_data = {}
        self.hand_config_data = {}

    def load_config(self):
        try:
            self.script_dir
        except:
            self.init_variables()
        
        # with open(os.path.join(root_url, facemesh_mapping_file), 'r') as input_file:
        with open(self.facemesh_mapping_file, 'r') as input_file:
            string_format = input_file.read()
            self.facemesh_config_data = json.loads(string_format)

        with open(self.hand_mapping_file, 'r') as input_file:
            string_format = input_file.read()
            self.hand_config_data = json.loads(string_format)

    def get_facemesh_config_data(self):
        if len(self.facemesh_config_data.keys()) == 0:
            self.load_config()
        return self.facemesh_config_data
    
    def get_hand_config_data(self):
        if len(self.hand_config_data.keys()) == 0:
            self.load_config()
        return self.hand_config_data

    def findObjectByNameAndType(self, name, obj_type):
        # DEPRICATED! Use findObjectFromOther() instead - it's much more accurate!
        objects = [obj for obj in bpy.context.scene.objects if obj.type == obj_type and obj.data.name == name]
        if len(objects) == 1:
            return objects[0]
        return objects[-1]
    
    def findObjectFromOther(self, other):
        # "other" is the bpy.context.scene.cyanic_* 
        other_uid = other.session_uid

        hits = list(filter(lambda x: x.data.session_uid == other_uid, bpy.context.scene.objects))
        return hits[0] # Should only throw an error if user deleted object
        # if len(hits) == 1:
        #     return hits[0] # Should only throw an error if user deleted object
        # elif len(hits) == 0:
        #     # self.report({'ERROR_INVALID_INPUT'}, 'No matching object. Was it deleted?')
        #     raise ValueError('No matching object. Was it deleted?')
        # else:
        #     # self.report({'ERROR_INVALID_INPUT'}, 'Multiple matching objects. Try "Make Local" to fix.')
        #     raise ValueError('Multiple matching objects. Try "Make Local" to fix.')

    def deselectAll(self):
        starting_mode = 'OBJECT'
        try:
            starting_mode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass # No object selected, likely in object mode already
        bpy.ops.object.mode_set(mode=starting_mode)

    def selectObjectByName(self, name, obj_type, clear_old=True):
        # DEPRICATED! Use selectObject now
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

    def selectObject(self, object, clear_old=True):
        if clear_old:
            self.deselectAll()
        try:
            bpy.context.view_layer.objects.active = object # Active object is what transform_apply is interacting with
            object.select_set(True)
            return object
        except:
            obj = self.findObjectFromOther(object)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            return obj