import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration
import av


st.set_page_config(page_title="Hand Gesture Recognition (Real-time)", page_icon="🖐️", layout="wide")


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


def count_fingers(hand_landmarks, handedness_label):
    """Counts fingers raised based on landmarks. Simple heuristic:
    - For index, middle, ring, pinky: tip y < pip y => raised
    - For thumb: compare x depending on left/right hand
    """
    landmarks = hand_landmarks.landmark

    # Finger tips and pips in Mediapipe
    tip_ids = [4, 8, 12, 16, 20]
    pip_ids = [None, 6, 10, 14, 18]  # Thumb has no direct PIP; handled separately

    fingers_up = 0

    # Thumb logic: compare x positions (since thumb points sideways)
    # For right hand, thumb is to the left when extended => tip_x < ip_x
    # For left hand, thumb is to the right when extended => tip_x > ip_x
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    if handedness_label.lower().startswith("right"):
        if thumb_tip.x < thumb_ip.x:
            fingers_up += 1
    else:
        if thumb_tip.x > thumb_ip.x:
            fingers_up += 1

    # Other 4 fingers: tip.y < pip.y means raised (note: y origin at top)
    for tip_id, pip_id in zip(tip_ids[1:], pip_ids[1:]):
        tip = landmarks[tip_id]
        pip = landmarks[pip_id]
        if tip.y < pip.y:
            fingers_up += 1

    return fingers_up


class HandGestureTransformer(VideoTransformerBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

            # Draw finger count and handedness
            for handedness, hand_landmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
                label = handedness.classification[0].label  # 'Left' or 'Right'
                num_up = count_fingers(hand_landmarks, label)

                # Compute a simple anchor point (wrist)
                h, w, _ = image.shape
                wrist = hand_landmarks.landmark[0]
                cx, cy = int(wrist.x * w), int(wrist.y * h)

                cv2.putText(
                    image,
                    f"{label} hand: {num_up} up",
                    (max(10, cx - 80), max(30, cy - 30)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

        return av.VideoFrame.from_ndarray(image, format="bgr24")


st.title("🖐️ Real-time Hand Gesture Recognition")
st.write("Detect hands and count raised fingers in real time using MediaPipe + OpenCV.")

with st.expander("Settings", expanded=False):
    stun_server = st.text_input("STUN server", value="stun:stun.l.google.com:19302")

rtc_configuration = RTCConfiguration({
    "iceServers": [{"urls": [stun_server]}]
})

webrtc_streamer(
    key="hand-gesture",
    mode=WebRtcMode.LIVE,
    video_transformer_factory=HandGestureTransformer,
    media_stream_constraints={"video": True, "audio": False},
    rtc_configuration=rtc_configuration,
)

