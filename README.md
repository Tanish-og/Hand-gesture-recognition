# Real-time Hand Gesture Recognition (Streamlit + MediaPipe)

Detect hands and count raised fingers in real time using MediaPipe and OpenCV, packaged as a Streamlit app (via streamlit-webrtc).

## Features
- Real-time webcam processing in the browser
- MediaPipe Hands landmark detection
- Simple finger counting heuristic (thumb + 4 fingers)
- Works locally with a single command

## Quick start
```bash
# (optional) create venv
python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```
Open the URL shown in the terminal (usually http://localhost:8501), allow camera access, and you should see hands and finger counts overlaid.

## Notes
- The heuristic uses y-positions for index/middle/ring/pinky and x-positions for thumb (accounting for handedness).
- If you encounter webcam permission issues, try an incognito window or a different browser.
- For deployment, ensure WebRTC is supported and reachable (ICE/STUN servers configured).

## Tech stack
- Streamlit, streamlit-webrtc
- MediaPipe, OpenCV, NumPy

## License
MIT