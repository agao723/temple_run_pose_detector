import cv2
import math
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

def detect_pose(image, pose, draw=False):
    """
    Detect poses and draw landmarks on screen

    Args:
        image (numpy array): image data of current frame
        pose: mp_pose.Pose object
        draw (boolean): display landmarks or not
    
    Returns:
        output_image: image data with landmarks displayed on it (or not)
        results: landmark data
    """

    output_image = image.copy()

    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = pose.process(imageRGB)

    if results.pose_landmarks and draw:
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks, 
                                    connections=mp_pose.POSE_CONNECTIONS,
                                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,255),
                                                                                        thickness=3, circle_radius=3),
                                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,0),
                                                                                        thickness=2, circle_radius=2))
    
    return output_image, results

def calculate_angle(a, b, c):
    """
    Calculates angle between three landmarks
    Args:
        a, b, c: x-y coordinates of landmarks to calculate angle between
    
    Returns:
        angle (float): angle between 0-360 degrees
    """

    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

def get_coords(landmark, results, height, width):
    """
    Returns x-y coordinates of landmark

    Args:
        landmark: landmark object
        height (int): height of window
        width (int): width of window
    
    Returns:
        x, y: coordinates
    """

    x = results.pose_landmarks.landmark[landmark].x * width
    y = results.pose_landmarks.landmark[landmark].y * height

    return x, y

def detect_start(img, results, draw=False):
    """
    Checks if current frame is in starting position

    Args:
        img: current frame
        results: landmark data
        draw (boolean): display start status or not
    Returns:
        output_image: updated frame
        start_status (string): "started" or "not started"
    """ 

    output_image = img.copy()
    height, width, _ = img.shape

    right_wrist = get_coords(mp_pose.PoseLandmark.RIGHT_WRIST, results, height, width)
    right_elbow = get_coords(mp_pose.PoseLandmark.RIGHT_ELBOW, results, height, width)
    right_shoulder = get_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER, results, height, width)

    left_wrist = get_coords(mp_pose.PoseLandmark.LEFT_WRIST, results, height, width)
    left_elbow = get_coords(mp_pose.PoseLandmark.LEFT_ELBOW, results, height, width)
    left_shoulder = get_coords(mp_pose.PoseLandmark.LEFT_SHOULDER, results, height, width)

    right_angle = calculate_angle(right_wrist, right_elbow, right_shoulder)
    left_angle = calculate_angle(left_wrist, left_elbow, left_shoulder)

    flat_angle_1 = calculate_angle(left_elbow, left_shoulder, right_shoulder)
    flat_angle_2 = calculate_angle(right_elbow, right_shoulder, left_shoulder)

    # check if arm angles are correct
    if 60 < right_angle < 120 and 240 < left_angle < 300 and 150 < flat_angle_1 < 210 and 150 < flat_angle_2 < 210:
        start_status = "started"
        color = (0, 255, 0)
    else:
        start_status = "not started"
        color = (0, 0, 255)
    
    if draw:
        cv2.putText(ouput_image, start_status, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1.5, color, 2)
    
    return output_image, start_status

def detect_end_pause(img, results):
    """
    Checks if current frame is in ending or pausing position

    Args:
        img: current frame
        results: landmark data
    Returns:
        output_image: updated frame
        start_status (string): "end" or "pause"
    """ 

    output_image = img.copy()
    height, width, _ = img.shape
    status = False

    # get coords of landmarks
    right_wrist = get_coords(mp_pose.PoseLandmark.RIGHT_WRIST, results, height, width)
    right_elbow = get_coords(mp_pose.PoseLandmark.RIGHT_ELBOW, results, height, width)
    right_shoulder = get_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER, results, height, width)

    left_wrist = get_coords(mp_pose.PoseLandmark.LEFT_WRIST, results, height, width)
    left_elbow = get_coords(mp_pose.PoseLandmark.LEFT_ELBOW, results, height, width)
    left_shoulder = get_coords(mp_pose.PoseLandmark.LEFT_SHOULDER, results, height, width)

    right_angle = calculate_angle(right_wrist, right_elbow, right_shoulder)
    left_angle = calculate_angle(left_wrist, left_elbow, left_shoulder)

    wrist_distance = math.hypot(left_wrist[0] - right_wrist[0],left_wrist[1] - right_wrist[1])
    crossed = right_wrist[0] > left_wrist[0]

    # print("distance: ", wrist_distance)
    # print("right angle: ", right_angle)
    # print("left angle: ", left_angle)

    # wrists need to be close and arms at certain angle
    if wrist_distance <= 150 and crossed and 300 < right_angle < 340 and 20 < left_angle < 60:
        status = "end"
    elif wrist_distance <= 70 and 330 < right_angle < 350 and 10 < left_angle < 30:
        status = "pause"

    return output_image, status


def detect_left_right(img, results, draw=False):
    """
    Checks what position player is standing in

    Args:
        img: current frame
        results: landmark data
        draw (boolean): display position or not
    Returns:
        output_image: updated frame
        pos (string): "left" or "center" or "right"
    """ 

    pos = None

    height, width, _ = img.shape
    output_image = img.copy()

    # x-coords of shoulder landmarks (flipped because camera is flipped)
    left_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width)
    right_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width)

    # Check if person is on the left half (both shoulders on the left)
    if right_x < width // 2 and left_x < width // 2:
        pos = 'left'
    # Check if person is on the right half
    elif right_x > width // 2 and left_x > width // 2:
        pos = 'right'
    # Check if person is in the middle (one shoulder on either side)
    elif right_x > width // 2 and left_x < width // 2:
        pos = 'center'
    
    if draw:
        cv2.putText(output_image, pos, (5, height - 10), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 2)
        cv2.line(output_image, (width//2, 0), (width//2, height), (255, 255, 255), 2)
    
    return output_image, pos

def detect_jump_crouch(img, results, MID_Y=250, draw=False):
    """
    Checks if player is jumping, crouching, or standing

    Args:
        img: current frame
        results: landmark data
        draw (boolean): display position or not
    Returns:
        output_image: updated frame
        pos (string): "Jumping" or "Crouching" or "Standing"
    """ 

    height, width, _ = img.shape

    output_image = img.copy()
        
    # y-coords
    right_shoulder_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)
    left_shoulder_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)
    right_wrist_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
    left_wrist_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)
    nose_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * height)

    wrists_y = abs(right_wrist_y + left_wrist_y) // 2
    shoulders_y = abs(right_shoulder_y + left_shoulder_y) // 2
    
    jump_threshold = MID_Y-15
    crouch_threshold = MID_Y+180
    
    # check if doing a jumping jack
    if (shoulders_y < jump_threshold and wrists_y < jump_threshold):
        posture = 'Jumping'
    # check if crouching
    elif (shoulders_y > crouch_threshold):
        posture = 'Crouching'
    else:
        posture = 'Standing'
        
    if draw:
        if posture == 'Standing':
            cv2.putText(output_image, posture, (5, height - 50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 2)
        else:
            cv2.putText(output_image, posture, (5, height - 50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 255, 0), 2)
        cv2.line(output_image, (0, MID_Y),(width, MID_Y),(255, 255, 255), 2)
        
    return output_image, posture