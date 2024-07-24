import bpy
import mathutils
import os

import importlib
from collections import namedtuple
Dependency = namedtuple("Dependency", ["module", "package", "name"])
dependencies = (
    Dependency(module="cv2", package="opencv-python", name=None),
    Dependency(module="mediapipe", package=None, name=None),
)
dependencies_imported = False

def import_module(module_name, global_name, reload=True):
    """
    Import a module.
    :param module_name: Module to import.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
        This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
        the global_name under which the module can be accessed.
    :raises: ImportError and ModuleNotFoundError
    """
    if global_name is None:
        global_name = module_name
    
    if global_name in globals():
        importlib.reload(globals()[global_name])
    else:
        # Attempt to import the module and assign it to globals dictionary. This allow to access the module under
        # the given name, just like the regular import would.
        globals()[global_name] = importlib.import_module(module_name)

def import_dependencies():
    global dependencies_imported
    if not dependencies_imported:
        for dependency in dependencies:
            import_module(dependency.module, dependency.name)
        dependencies_imported = True


class GenRigFromMetaRigOperator(bpy.types.Operator):
    """Select the rig generated from the metarig"""
    bl_idname = "object.genrigfrommetarig"
    bl_label = "GenRigFromMetaRig"

    def execute(self, context):
        import_dependencies()
        if context.scene.cyanic_rigify_gen_rig is None:
            self.report({'ERROR_INVALID_INPUT'}, 'No Rigify metarig selected')
            return {'CANCELLED'}

        # Ideally, I'd LOVE to automatically press the "Generate Rig" button for the user.
        if context.scene.cyanic_rigify_gen_rig.rigify_target_rig is None:
            self.report({'ERROR_INVALID_INPUT'}, "Rigify metarig hasn't generated a rig")
            return {'CANCELLED'}

        context.scene.cyanic_rigify_gen_rig = context.scene.cyanic_rigify_gen_rig.rigify_target_rig
        return {'FINISHED'}


class MocapOperator(bpy.types.Operator):
    """Generate mocap"""
    bl_idname = "object.mocap"
    bl_label = "Mocap"

    # data_dir = 'data'
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.split(script_dir)[0], 'data')
    armature = None

    # Note: The Mediapipe Holistic detection has been "coming soon!" for too long, so I'm basing this off the Legacy Solution
    # "Coming Soon" page - https://ai.google.dev/edge/mediapipe/solutions/vision/holistic_landmarker
    # Legacy Solution page - https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/holistic.md
    def execute(self, context):
        self.armature = context.scene.cyanic_rigify_gen_rig
        # if self.armature is None:
        #     # Not ready to rig
        #     self.report({'ERROR_INVALID_INPUT'}, "Rig not provided")
        #     return {'CANCELLED'}

        self.holistic_processing(context)



    def holistic_processing(self, context):
        # Get the file/live
        source_type = context.scene.cyanic_source_type # image/video
        source_input = context.scene.cyanic_source_input # file/webcam
        file_path = context.scene.cyanic_mocap_file_path # file

        # TODO: REMOVE LATER - FOR TESTING ONLY
        if file_path is None or len(file_path) == 0:
            context.scene.cyanic_mocap_file_path = 'data/test_pose.jpg'
            file_path = context.scene.cyanic_mocap_file_path

        mp_holistic = mediapipe.solutions.holistic
        # Set what kind of media is being used
        static_image_mode = True 
        model_complexity = 2 # 0 for fastest, 2 for most detailed, 1 for middle ground
        smooth_landmarks = True # If multiple images, it'll reduce jitter. Ignored if static_image_mode is True
        refine_face_landmarks = False # Used to increase details around the eyes and lips, and add irises
        min_detection_confidence = 0.5
        min_tracking_confidence = 0.5

        if source_type == 'image_mode':
            # Adjust settings for static content
            static_image_mode = True
            model_complexity = 2
            refine_face_landmarks = True

            image = None

            if source_input == 'file_input':
                # Read a single image
                try:
                    image = cv2.imread(file_path)
                except:
                    self.report({'ERROR_INVALID_INPUT'}, "Could not read image file")
                    return {'CANCELLED'}

            elif source_input == 'webcam_input':    
                # TODO: Add a way to get a still image from webcam, probably using a countdown timer
                pass

            with mp_holistic.Holistic(
                static_image_mode=static_image_mode,
                model_complexity=model_complexity,
                refine_face_landmarks=refine_face_landmarks,
                smooth_landmarks=smooth_landmarks
            ) as holistic:
                image_height, image_width, _ = image.shape
                # Convert the BGR image to RGB before processing.
                results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                self.landmark_frame_to_pose(results, image_width, image_height)


        elif source_type == 'video_mode':
            # Adjust settings for video content
            static_image_mode = False
            refine_face_landmarks = True
            min_detection_confidence = 0.5
            min_tracking_confidence = 0.5

            cap = None

            if source_input == 'file_input':
                model_complexity = 2 # From file - make it detailed
                try:
                    cap = cv2.VideoCapture(file_path)
                except:
                    self.report({'ERROR_INVALID_INPUT'}, "Could not read video file")
                    return {'CANCELLED'}
                
            elif source_input == 'webcam_input':
                model_complexity = 0 # Realtime - make it fast
                cap = cv2.VideoCapture(0) # Selects the default webcam

            with mp_holistic.Holistic(
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
                model_complexity=model_complexity,
                refine_face_landmarks=refine_face_landmarks,
                smooth_landmarks=smooth_landmarks
            ) as holistic:
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        # Ignore the empty camera frame
                        break
                    
                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    image.flags.writeable = False
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image_height, image_width, _ = image.shape
                    results = holistic.process(image)

                    self.landmark_frame_to_pose(results, image_width, image_height)


        return {'FINISHED'}

    def get_vector(self, landmark, image_width, image_height, scaler, offset=None):
        if offset:
            blender_x = offset.x + (landmark.x * image_width / scaler)
            blender_z = offset.z + (-1 * landmark.y * image_height / scaler)
            blender_y = offset.y + (landmark.z * image_width / scaler) # "The magnitude of z uses roughly the same scale as x."
            return mathutils.Vector((blender_x, blender_y, blender_z))
        else:
            blender_x = landmark.x * image_width / scaler
            blender_z = landmark.y * -1 * image_height / scaler
            blender_y = landmark.z * image_width / scaler # "The magnitude of z uses roughly the same scale as x."
            return mathutils.Vector((blender_x, blender_y, blender_z))

    def add_obj_to_collection(self, object, collection):
            # new_point = bpy.context.active_object
            for coll in object.users_collection: # Remove from other collections
                coll.objects.unlink(object)
            collection.objects.link(object)

    def landmark_frame_to_pose(self, mp_results, image_width, image_height, frame=-1):
        # frame -1 means append it after the last frame.
        # To prototype, just create empties at the landmark locations

        # mp_results.pose_world_landmarks.landmark
        # mp_results.right_hand_landmarks.landmark
        # mp_results.left_hand_landmarks.landmark
        # mp_results.face_landmarks.landmark
        print('Ready to landmark')
        scaler = 200 # How to set scale this?

        right_wrist_origin = mathutils.Vector((0,0,0))
        left_wrist_origin = mathutils.Vector((0,0,0))
        head_origin = mathutils.Vector((0,0,0))

        scale = (0.01,0.01,0.01)

        pose_collection = bpy.context.blend_data.collections.new(name='Pose')
        bpy.context.collection.children.link(pose_collection)
        for index, landmark in enumerate(mp_results.pose_world_landmarks.landmark):
            # 0,0,0 = between the hips
            v = self.get_vector(landmark, image_width, image_height, scaler)

            if index == 0:
                head_origin = v
            if index == 15:
                left_wrist_origin = v
            if index == 16:
                right_wrist_origin = v

            face_indexes = [1,2,3,4,5,6,7,8,9,10]
            left_hand_indexes = [17,19,21]
            right_hand_indexes = [18,20,22]
            if index in face_indexes or index in left_hand_indexes or index in right_hand_indexes:
                # Skip drawing
                # continue
                pass 

            # bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=v, scale=scale)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=v)
            bpy.context.active_object.name = 'Pose.%s' % index
            self.add_obj_to_collection(bpy.context.active_object, pose_collection)


        right_hand_collection = bpy.context.blend_data.collections.new(name='Hand.R')
        bpy.context.collection.children.link(right_hand_collection)
        v = self.get_vector(mp_results.right_hand_landmarks.landmark[0], image_width, image_height, scaler)
        if v != mathutils.Vector((0.0, 0.0, 0.0)):
            # Correct the offset
            right_wrist_origin = right_wrist_origin - (v - mathutils.Vector((0.0, 0.0, 0.0)))
        for landmark in mp_results.right_hand_landmarks.landmark:
            v = self.get_vector(landmark, image_width, image_height, scaler, right_wrist_origin)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=v, scale=scale)
            bpy.context.active_object.name = 'Hand.R.%s' % index
            self.add_obj_to_collection(bpy.context.active_object, right_hand_collection)


        left_hand_collection = bpy.context.blend_data.collections.new(name='Hand.L')
        bpy.context.collection.children.link(left_hand_collection)
        v = self.get_vector(mp_results.left_hand_landmarks.landmark[0], image_width, image_height, scaler)
        if v != mathutils.Vector((0.0, 0.0, 0.0)):
            # Correct the offset
            left_wrist_origin = left_wrist_origin - (v - mathutils.Vector((0.0, 0.0, 0.0)))
        for landmark in mp_results.left_hand_landmarks.landmark:
            v = self.get_vector(landmark, image_width, image_height, scaler, left_wrist_origin)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=v, scale=scale)
            bpy.context.active_object.name = 'Hand.L.%s' % index
            self.add_obj_to_collection(bpy.context.active_object, left_hand_collection)


        face_collection = bpy.context.blend_data.collections.new(name='Face')
        bpy.context.collection.children.link(face_collection)
        v = self.get_vector(mp_results.face_landmarks.landmark[1], image_width, image_height, scaler) # Point 1 is the tip of the nose
        if v != mathutils.Vector((0.0, 0.0, 0.0)):
            # Correct the offset
            head_origin = head_origin - (v - mathutils.Vector((0.0, 0.0, 0.0)))
        for landmark in mp_results.face_landmarks.landmark:
            v = self.get_vector(landmark, image_width, image_height, scaler, head_origin)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=v, scale=scale)
            bpy.context.active_object.name = 'Face.%s' % index
            self.add_obj_to_collection(bpy.context.active_object, face_collection)
        