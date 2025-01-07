import cv2
import pyautogui
import argparse
from pose_detection import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fullscreen', required=False, default='False',
                        help="Play in fullscreen mode or not")
    args = parser.parse_args()
    fullscreen = (args.fullscreen == 'True')

    pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, 
                            min_tracking_confidence=0.6, model_complexity=1)

    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,360)
    cap.set(5,30)

    # game variables
    game_started = False
    paused = False
    x_pos = 0
    y_pos = 0
    MID_Y = None
    start_frames = 0
    end_frames = 0
    pause_frames = 0
    countdown = 20

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        frame, results = detect_pose(frame, pose_video, draw=game_started)

        if results.pose_landmarks:
            # movement / starting the game
            if game_started:
                frame, pos = detect_left_right(frame, results, draw=True)
                if (pos == 'left' and x_pos != -1) or (pos == 'center' and x_pos == 1):
                    pyautogui.press('left')
                    x_pos -= 1               
                elif (pos == 'right' and x_pos != 1) or (pos == 'center' and x_pos == -1):
                    pyautogui.press('right')
                    x_pos += 1
                if detect_start(frame, results)[1] == "started":
                    pyautogui.click(x=700, y=260, button='left')
                    pyautogui.press('space')
                    if paused:
                        paused = False
            else:
                cv2.putText(frame, 'Put your hands up to start the game!', (80, frame_height // 2), cv2.FONT_HERSHEY_COMPLEX,
                            1.5, (255, 255, 255), 2)
                
            # starting the game for the first time
            if detect_start(frame, results)[1] == "started":
                start_frames += 1
                if start_frames == countdown:
                    if not(game_started):
                        game_started = True
                        # set jump threshold
                        left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame_height)
                        right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame_height)
                        MID_Y = abs(left_y + right_y) // 2
                        pyautogui.click(x=700, y=260, button='left')
                        pyautogui.press('space')
                        paused = False
            else:
                start_frames = 0
            # closing the game
            if detect_end_pause(frame, results)[1] == "end":
                end_frames += 1
                if end_frames == countdown:
                    break
            # pausing the game
            elif detect_end_pause(frame, results)[1] == "pause":
                if not paused:
                    if fullscreen:
                        pyautogui.click(x=1360, y=720, button='left')
                    else:
                        pyautogui.press('esc')
                    paused = True
            else:
                end_frames = 0
                pause_frames = 0
            # jumping and crouching
            if MID_Y:
                frame, posture = detect_jump_crouch(frame, results, MID_Y)
                if posture == 'Jumping' and y_pos == 0:
                    pyautogui.press('up')
                    y_pos += 1 
                elif posture == 'Crouching' and y_pos == 0:
                    pyautogui.press('down')
                    y_pos -= 1
                elif posture == 'Standing' and y_pos != 0:
                    y_pos = 0
        else:
            start_frames = 0
            end_frames = 0
            pause_frames = 0
        
        cv2.imshow("Feed", frame)

        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()