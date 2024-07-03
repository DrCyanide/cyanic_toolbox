import numpy as np
import mediapipe as mp
import cv2
import time

pose_model_path = 'data/pose_landmarker_heavy.task' # https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task
hand_model_path = 'data/hand_landmarker.task' # https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
face_model_path = 'data/face_landmarker.task' # https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
reference_path = 'data/test_pose.jpg'

# This method works for one system at a time - like just PoseLandmarker, HandLandmarker, or FaceLandmarker
def SplitProcessing():
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    pose_options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=pose_model_path),
        running_mode=VisionRunningMode.IMAGE)

    HandLandmarker = mp.tasks.vision.HandLandmarker
    hand_options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=hand_model_path),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=2
    )

    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    face_options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=face_model_path),
        running_mode=VisionRunningMode.IMAGE
    )

    split_start = time.time()

    mp_image = mp.Image.create_from_file(reference_path)

    with PoseLandmarker.create_from_options(pose_options) as landmarker:
        pose_landmarker_result = landmarker.detect(mp_image)
    #     # pose_landmarker_result.pose_world_landmarks[frame][index]
    #     print(pose_landmarker_result.pose_world_landmarks[0][0])
    #     print(dir(pose_landmarker_result))

    with HandLandmarker.create_from_options(hand_options) as landmarker:
        hand_landmarker_results = landmarker.detect(mp_image)

    with FaceLandmarker.create_from_options(face_options) as landmarker:
        face_landmarker_results = landmarker.detect(mp_image)

    split_stop = time.time()
    print('Split time') 
    print(split_stop - split_start)
    # Took about 0.412s on my system if including loading the models
    # Took about 0.370s if models loaded before timer


def HolisticProcessing():
    holistic_start = time.time()
    IMAGE_FILES = [reference_path]

    mp_holistic = mp.solutions.holistic

    # print(dir(mp_holistic))
    # print('\tPose Landmarks')
    # print(dir(mp_holistic.PoseLandmark))
    # print('\tHand Landmarks')
    # print(dir(mp_holistic.HandLandmark))
    # print('\tFace?')
    # print(dir(mp_holistic.FaceLandmark))

    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=False,
        refine_face_landmarks=True # "refine the landmark coordinates around the eyes and lips, and output additional landmarks around the irises"
        ) as holistic:
        
        for idx, file in enumerate(IMAGE_FILES):
            image = cv2.imread(file)
            image_height, image_width, _ = image.shape
            # Convert the BGR image to RGB before processing.
            results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            holistic_end = time.time()
            print('Holistic:')
            print(holistic_end - holistic_start)
            # Took about 0.244s - 0.283s on my system - much faster than the split version

            for landmark in results.pose_world_landmarks.landmark:
                x = landmark.x * image_width
                y = landmark.y * image_height
                z = landmark.z * image_width # "The magnitude of z uses roughly the same scale as x."
                print('(%s, %s, %s)' % (x, y, z))
            # print(dir(results))
            # if results.pose_world_landmarks:
            #     # pose_world_landmarks
            #     # right_hand_landmarks
            #     # left_hand_landmarks
            #     # face_landmarks

            #     print('Pose Nose:')
            #     print(results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * image_width)
            #     print(results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * image_height)
            #     print(results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].z * image_width) # "The magnitude of z uses roughly the same scale as x."

            #     print('Right index:')
            #     print(results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].x * image_width)
            #     print(results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].y * image_height)
            #     print(results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].z * image_width)
                
            #     print('Left index:')
            #     print(results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].x * image_width)
            #     print(results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].y * image_height)
            #     print(results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].z * image_width)


            #     print('Face')
            #     # print(results.face_landmarks.landmark[1].x * image_width)
            #     # print(results.face_landmarks.landmark[1].y * image_height)
            #     # print(results.face_landmarks.landmark[1].z * image_width)
            #     print(results.face_landmarks.landmark[1].x)
            #     print(results.face_landmarks.landmark[1].y)
            #     print(results.face_landmarks.landmark[1].z)

if __name__ == '__main__':
    SplitProcessing()
    HolisticProcessing()