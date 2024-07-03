import bpy
import os
import json
import math

try:
    import numpy as np
    import mediapipe as mp
    import skimage
    from skimage.transform import PiecewiseAffineTransform, warp
except:
    # One or more dependency still needed
    import pip
    modules = [
        'numpy',
        'mediapipe',
        'scikit-image', #skimage
    ]

    for mod in modules:
        pip.main(['install', mod, '--user'])
    
    import numpy as np
    import mediapipe as mp
    import skimage
    from skimage.transform import PiecewiseAffineTransform, warp


class FaceImg2FacemeshOperator(bpy.types.Operator):
    """Convert image to face mesh"""
    bl_idname = "object.faceimg2facemesh"
    bl_label = "FaceImg2Facemesh"

    # data_dir = 'data'
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.split(script_dir)[0], 'data')

    img_path = ''
    save_dir = '' # Use same dir as the image path? Or prompt for a new path? 
    obj_name = ''
    texture_name = ''
    uv_map = None

    def execute(self, context):
        # Read img from context.scene.cyanic_img_path
        self.img_path = context.scene.cyanic_img_path
        self.save_dir = os.path.split(self.img_path)[0] # Save OBJ to the same directory as the source image
        filename =  os.path.splitext(os.path.basename(self.img_path))[0] # the name without the extension
        self.obj_name =  "%s.obj" % filename
        self.texture_name = ".%s_texture.jpg" % filename

        self.prep_uv_map()
        response = self.landmark_detection()
        # Because mediapipe is particular about how the PNG is formatted, it might fail - even with rgba2rgb
        if response is not None:
            return response
        self.landmarks_to_3d()

        # Import finished file into Blender
        bpy.ops.wm.obj_import(filepath=os.path.join(self.save_dir, self.obj_name))
        # The object is now the active object, assign it to cyanic_facemesh
        context.scene.cyanic_facemesh = bpy.context.view_layer.objects.active.data # Gets the active mesh (data) instead of just the object
        return {'FINISHED'}

    # borrowed from https://github.com/YadiraF/DECA/blob/f84855abf9f6956fb79f3588258621b363fa282c/decalib/utils/util.py
    def load_obj(self, obj_filename):
        """ Ref: https://github.com/facebookresearch/pytorch3d/blob/25c065e9dafa90163e7cec873dbb324a637c68b7/pytorch3d/io/obj_io.py
        Load a mesh from a file-like object.
        """
        with open(obj_filename, 'r') as f:
            lines = [line.strip() for line in f]

        verts, uvcoords = [], []
        faces, uv_faces = [], []
        # startswith expects each line to be a string. If the file is read in as
        # bytes then first decode to strings.
        if lines and isinstance(lines[0], bytes):
            lines = [el.decode("utf-8") for el in lines]

        for line in lines:
            tokens = line.strip().split()
            if line.startswith("v "):  # Line is a vertex.
                vert = [float(x) for x in tokens[1:4]]
                if len(vert) != 3:
                    msg = "Vertex %s does not have 3 values. Line: %s"
                    raise ValueError(msg % (str(vert), str(line)))
                verts.append(vert)
            elif line.startswith("vt "):  # Line is a texture.
                tx = [float(x) for x in tokens[1:3]]
                if len(tx) != 2:
                    raise ValueError(
                        "Texture %s does not have 2 values. Line: %s" % (str(tx), str(line))
                    )
                uvcoords.append(tx)
            elif line.startswith("f "):  # Line is a face.
                # Update face properties info.
                face = tokens[1:]
                face_list = [f.split("/") for f in face]
                for vert_props in face_list:
                    # Vertex index.
                    faces.append(int(vert_props[0]))
                    if len(vert_props) > 1:
                        if vert_props[1] != "":
                            # Texture index is present e.g. f 4/1/1.
                            uv_faces.append(int(vert_props[1]))

        verts = np.array(verts)
        uvcoords = np.array(uvcoords)
        faces = np.array(faces); faces = faces.reshape(-1, 3) - 1
        uv_faces = np.array(uv_faces); uv_faces = uv_faces.reshape(-1, 3) - 1
        return (
            verts,
            uvcoords,
            faces,
            uv_faces
        )
    
    # borrowed from https://github.com/YadiraF/DECA/blob/f84855abf9f6956fb79f3588258621b363fa282c/decalib/utils/util.py
    def write_obj(self, 
                obj_name,
                vertices,
                faces,
                texture_name = "texture.jpg",
                colors=None,
                texture=None,
                uvcoords=None,
                uvfaces=None
                ):
        ''' Save 3D face model with texture. 
        Ref: https://github.com/patrikhuber/eos/blob/bd00155ebae4b1a13b08bf5a991694d682abbada/include/eos/core/Mesh.hpp
        Args:
            obj_name: str
            vertices: shape = (nver, 3)
            colors: shape = (nver, 3)
            faces: shape = (ntri, 3)
            texture: shape = (uv_size, uv_size, 3)
            uvcoords: shape = (nver, 2) max value<=1
        '''
        if os.path.splitext(obj_name)[-1] != '.obj':
            obj_name = obj_name + '.obj'
        mtl_name = obj_name.replace('.obj', '.mtl')
        texture_name
        material_name = 'FaceTexture'

        faces = faces.copy()
        # mesh lab start with 1, python/c++ start from 0
        faces += 1

        # write obj
        with open(obj_name, 'w') as f:
            # first line: write mtlib(material library)
            if texture is not None:
                f.write('mtllib %s\n\n' % os.path.basename(mtl_name))

            # write vertices
            if colors is None:
                for i in range(vertices.shape[0]):
                    f.write('v {} {} {}\n'.format(vertices[i, 0], vertices[i, 1], vertices[i, 2]))
            else:
                for i in range(vertices.shape[0]):
                    f.write('v {} {} {} {} {} {}\n'.format(vertices[i, 0], vertices[i, 1], vertices[i, 2], colors[i, 0], colors[i, 1], colors[i, 2]))

            # write uv coords
            if texture is None:
                for i in range(faces.shape[0]):
                    f.write('f {} {} {}\n'.format(faces[i, 2], faces[i, 1], faces[i, 0]))
            else:
                for i in range(uvcoords.shape[0]):
                    f.write('vt {} {}\n'.format(uvcoords[i,0], uvcoords[i,1]))
                f.write('usemtl %s\n' % material_name)
                # write f: ver ind/ uv ind
                uvfaces = uvfaces + 1
                for i in range(faces.shape[0]):
                    f.write('f {}/{} {}/{} {}/{}\n'.format(
                        faces[i, 0], uvfaces[i, 0],
                        faces[i, 1], uvfaces[i, 1],
                        faces[i, 2], uvfaces[i, 2]
                    )
                    )
                # write mtl
                with open(mtl_name, 'w') as f:
                    f.write('newmtl %s\n' % material_name)
                    s = 'map_Kd {}\n'.format(os.path.basename(texture_name)) # map to image
                    f.write(s)
                try:
                    skimage.io.imsave(texture_name, texture)
                except Exception as e:
                    # There's still an alpha channel in the image
                    skimage.io.imsave(texture_name, skimage.color.rgba2rgb(texture))

    def normalize_keypoints(self, keypoints3d):
        # Rotates and centers the points.
        # One of the rotations is a little too far
        #  Landmarks labeled
        #  https://github.com/google/mediapipe/blob/a908d668c730da128dfa8d9f6bd25d519d006692/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
        center = keypoints3d[0]
        keypoints3d = keypoints3d - center # This centering is undone by some later step
        # axis1 = keypoints3d[165] - keypoints3d[391] # 165 = left side between nose and lip, # right side between nose and lip (one vertex off center)
        # axis2 = keypoints3d[2] - keypoints3d[0] # 2 = below nose, 0 = above lip (only 1 vertex apart)
        axis1 = keypoints3d[454] - keypoints3d[234] # side of face to side of face
        axis2 = keypoints3d[10] - keypoints3d[152] # forehead to chin
        axis3 = np.cross(axis2,axis1)
        axis3 = axis3/np.linalg.norm(axis3)
        axis2 = axis2/np.linalg.norm(axis2)
        axis1 = np.cross(axis3, axis2) # Should be redundant
        axis1 = axis1/np.linalg.norm(axis1)
        U = np.array([axis3,axis2,axis1]) # Would changing this order help correctly orient the object?
        keypoints3d = keypoints3d.dot(U)
        keypoints3d = keypoints3d - keypoints3d.mean(axis=0) # Doesn't seem to make a difference

        return keypoints3d

    def rotate_around_origin(self, keypoints3d, opp_side, adj_side, angle):
        for row in keypoints3d:
            a0 = math.cos(angle) * row[opp_side] - math.sin(angle) * row[adj_side]
            a1 = math.cos(angle) * row[adj_side] + math.sin(angle) * row[opp_side]
            row[opp_side] = a0
            row[adj_side] = a1
        return keypoints3d

    def align_keypoints_to_grid(self, keypoints3d):
        # Center at keypoints3d[0]
        # Put chin and forehead (keypoints3d[152] and keypoints3d[10]) on Z axis
        # Put left and right cheeks (keypoints3d[234] and keypoints3d[454]) on X axis
        #  Landmarks labeled
        #  https://github.com/google/mediapipe/blob/a908d668c730da128dfa8d9f6bd25d519d006692/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
        # If needed, center the face 
        if np.count_nonzero(keypoints3d[0]) > 0: # Check if the values are all zeros
            keypoints3d = keypoints3d - keypoints3d[0]

        # Rotate the face left-to-right to be straight up-and-down
        adj_side, opp_side = keypoints3d[10][1], keypoints3d[10][2] # Forehead
        angle = math.atan2(opp_side, adj_side)
        keypoints3d = self.rotate_around_origin(keypoints3d, 2, 1, angle)

        # Rotate the face forward-and-back
        adj_side, opp_side = keypoints3d[9][1], keypoints3d[9][0] # Center of brow
        angle = math.atan2(opp_side, adj_side)
        keypoints3d = self.rotate_around_origin(keypoints3d, 0, 1, angle)

        # Rotate the face to be looking straight ahead
        face_left = keypoints3d[454]
        face_right = keypoints3d[234]
        # Need a midpoint between these two to rotate between
        middle = (face_left + face_right) / 2
        keypoints3d = keypoints3d - middle
        # Re-determine the left/right side
        face_left = keypoints3d[454]
        face_right = keypoints3d[234]
        adj_side, opp_side = face_left[0], face_left[2]
        angle = math.atan2(opp_side, adj_side)
        keypoints3d = self.rotate_around_origin(keypoints3d, 2, 0, angle)
        
        # Return center it's original location
        keypoints3d = keypoints3d - keypoints3d[0]
        return keypoints3d

    def prep_uv_map(self):
        uv_path = os.path.join(self.data_dir, "uv_map.json") # taken from https://github.com/spite/FaceMeshFaceGeometry/blob/353ee557bec1c8b55a5e46daf785b57df819812c/js/geometry.js
        uv_map_dict = json.load(open(uv_path))
        self.uv_map = np.array([ (uv_map_dict["u"][str(i)],uv_map_dict["v"][str(i)]) for i in range(468)])

    def landmark_detection(self):
        self.img = skimage.io.imread(self.img_path)

        H,W,_ = self.img.shape
        # run facial landmark detection
        with mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                refine_landmarks=True,
                max_num_faces=1,
                min_detection_confidence=0.5) as face_mesh:
            
            # TODO: Just check the extension of self.img_path first to see if it's a PNG

            try:
                results = face_mesh.process(self.img)
            except:
                # PNG was probaly provided, try to convert to JPG
                try:
                    # tmp_path = 'converted.jpg'
                    # png_img = skimage.io.imread(self.img_path)
                    # rgb_img = skimage.color.rgba2rgb(png_img)
                    # skimage.io.imsave(tmp_path, rgb_img, quality=100)
                    # self.img = skimage.io.imread(tmp_path)
                    # os.remove(tmp_path) # Cleanup
                    # results = face_mesh.process(self.img)

                    self.img = skimage.color.rgba2rgb(self.img)
                    results = face_mesh.process(self.img)
                except:
                    # raise Exception('Unable to use a PNG, and unable to automatically convert PNG to JPG')
                    self.report({'ERROR_INVALID_INPUT'}, 'Unable to use this image, please try a JPG/JPEG image instead')
                    return {'CANCELLED'}

        # Only support one face per image, ignores any other faces detected
        face_landmarks = results.multi_face_landmarks[0]
        self.keypoints = np.array([(W*point.x,H*point.y) for point in face_landmarks.landmark[0:468]])#after 468 is iris or something else

        # The X, Y, and Z coords are normalized to 0.0 to 1.0 for the width and height of the image (Z is at the same scale as X).
        # To restore the face to it's original ratio, the X and Z coordinates need to be scaled by the ratio of width to height
        # See https://google.github.io/mediapipe/solutions/face_mesh#output for more details

        width_ratio = W / H
        self.keypoints3d = np.array([(width_ratio * point.x, point.y, width_ratio * point.z) for point in face_landmarks.landmark[0:468]])

    def prep_texture(self):
        H_new,W_new = 512,512
        keypoints_uv = np.array([(W_new*x, H_new*y) for x,y in self.uv_map])

        tform = PiecewiseAffineTransform()
        tform.estimate(keypoints_uv,self.keypoints)
        self.texture = warp(self.img, tform, output_shape=(H_new,W_new))
        self.texture = (255*self.texture).astype(np.uint8)

    def landmarks_to_3d(self):
        obj_filename = os.path.join(self.data_dir, "canonical_face_model.obj")
        canonical_verts,uvcoords,faces,uv_faces = self.load_obj(obj_filename)

        # keypoints3d already has a face that's more round than the original
        vertices = self.normalize_keypoints(self.keypoints3d)
        # Rotate the vertices so the face isn't at an odd angle
        vertices = self.align_keypoints_to_grid(vertices)

        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        self.prep_texture()

        # borrowed from https://github.com/YadiraF/PRNet/blob/master/utils/write.py
        self.write_obj(os.path.join(self.save_dir, self.obj_name),
                    vertices,
                    faces,
                    os.path.join(self.save_dir, self.texture_name),
                    texture=self.texture,
                    uvcoords=uvcoords,
                    uvfaces=uv_faces,
                    )