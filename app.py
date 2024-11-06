import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import random
import time

# Initialize Mediapipe Hands for hand tracking
mp_hands = mp.solutions.hands

# Initialize session state variables
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
    st.session_state.computer_score = 0
    st.session_state.round_number = 1
    st.session_state.game_state = 'menu'
    st.session_state.countdown = 3
    st.session_state.winning_score = 5
    st.session_state.last_result = ''
    st.session_state.player_choice = ''
    st.session_state.computer_choice = ''
    st.session_state.countdown_active = False
    st.session_state.timer_start = None

# Function to classify hand gestures based on landmarks
def classify_hand_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_is_open = thumb_tip.x < thumb_ip.x

    fingers_open = [
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y <
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y <
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y,
    ]
    open_count = sum(fingers_open)

    # Determine the gesture
    if open_count == 2 and fingers_open[0] and fingers_open[1]:
        return 'Scissors'
    elif open_count == 4:
        return 'Paper'
    elif open_count == 0:
        return 'Rock'
    else:
        return 'Unknown'

# Function to reset the game state
def reset_game():
    st.session_state.player_score = 0
    st.session_state.computer_score = 0
    st.session_state.round_number = 1
    st.session_state.game_state = 'menu'
    st.session_state.countdown = 3
    st.session_state.last_result = ''
    st.session_state.player_choice = ''
    st.session_state.computer_choice = ''
    st.session_state.countdown_active = False
    st.session_state.timer_start = None

# Enhanced UI Elements
st.set_page_config(page_title="Rock Paper Scissors Game", page_icon="✊🤚✌️")
st.markdown("""
    <style>
    body {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .title {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        color: #FF6347;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 24px;
        color: #FFFFFF;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    .countdown {
        text-align: center;
        font-size: 60px;
        color: #FFA07A;
    }
    .result {
        text-align: center;
        font-size: 36px;
        color: #32CD32;
    }
    .result-loss {
        text-align: center;
        font-size: 36px;
        color: #FF4500;
    }
    .scoreboard {
        text-align: center;
        font-size: 24px;
        color: #FFFFFF;
    }
    .game-over {
        text-align: center;
        font-size: 40px;
        color: #FFD700;
    }
    .button {
        display: flex;
        justify-content: center;
    }
    .btn {
        background-color: #FF6347;
        color: white;
        padding: 15px 30px;
        font-size: 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .btn:hover {
        background-color: #FF4500;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='title'>Rock Paper Scissors</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Play against the computer using your webcam!</div>", unsafe_allow_html=True)

if st.session_state.game_state == 'menu':
    st.markdown("<div style='text-align: center;'><strong>Select Winning Score:</strong></div>", unsafe_allow_html=True)
    st.session_state.winning_score = st.slider('', min_value=1, max_value=10, value=5, step=1)
    if st.button('Start Game'):
        st.session_state.game_state = 'countdown'
        st.session_state.countdown_active = True
        st.session_state.timer_start = time.time()
elif st.session_state.game_state == 'countdown':
    if st.session_state.countdown_active:
        elapsed_time = int(time.time() - st.session_state.timer_start)
        st.session_state.countdown = 3 - elapsed_time
        if st.session_state.countdown > 0:
            st.markdown(f"<div class='countdown'>Get Ready: {st.session_state.countdown}</div>", unsafe_allow_html=True)
        else:
            st.session_state.countdown_active = False
            st.session_state.game_state = 'playing'
    else:
        st.session_state.game_state = 'playing'
elif st.session_state.game_state == 'playing':
    st.markdown(f"<div class='subtitle'>Round {st.session_state.round_number}</div>", unsafe_allow_html=True)
    st.write('Show your hand gesture for Rock ✊, Paper 🤚, or Scissors ✌️!')
    img_file_buffer = st.camera_input("Capture your move")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        np_arr = np.frombuffer(bytes_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75) as hands:
            results = hands.process(frame_rgb)
            player_choice = 'Unknown'

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    player_choice = classify_hand_gesture(hand_landmarks)
                    mp.solutions.drawing_utils.draw_landmarks(frame_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if player_choice in ['Rock', 'Paper', 'Scissors']:
                computer_choice = random.choice(['Rock', 'Paper', 'Scissors'])
                if player_choice == computer_choice:
                    result = "It's a tie!"
                    result_class = 'result'
                elif (player_choice == 'Rock' and computer_choice == 'Scissors') or \
                     (player_choice == 'Paper' and computer_choice == 'Rock') or \
                     (player_choice == 'Scissors' and computer_choice == 'Paper'):
                    result = "You win this round!"
                    result_class = 'result'
                    st.session_state.player_score += 1
                else:
                    result = "Computer wins this round!"
                    result_class = 'result-loss'
                    st.session_state.computer_score += 1

                st.session_state.player_choice = player_choice
                st.session_state.computer_choice = computer_choice
                st.session_state.last_result = result
                st.image(frame_rgb, caption='Your Move', use_column_width=True)

                st.markdown(f"<div class='scoreboard'><strong>You chose:</strong> {player_choice} | <strong>Computer chose:</strong> {computer_choice}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='{result_class}'>{result}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='scoreboard'>Score: <strong>You {st.session_state.player_score}</strong> - <strong>Computer {st.session_state.computer_score}</strong></div>", unsafe_allow_html=True)

                st.session_state.round_number += 1
                if st.session_state.player_score >= st.session_state.winning_score or st.session_state.computer_score >= st.session_state.winning_score:
                    st.session_state.game_state = 'game_over'
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button('Next Round'):
                            st.session_state.game_state = 'countdown'
                            st.session_state.countdown = 3
                            st.session_state.countdown_active = True
                            st.session_state.timer_start = time.time()
                    with col2:
                        if st.button('Quit Game'):
                            reset_game()
            else:
                st.write('Could not recognize your gesture. Please try again.')
                st.image(frame_rgb, caption='Your Move', use_column_width=True)
                if st.button('Try Again'):
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.countdown_active = True
                    st.session_state.timer_start = time.time()
else:
    if st.session_state.player_score > st.session_state.computer_score:
        st.markdown("<div class='game-over'>🎉 Congratulations, You Won the Game! 🎉</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='game-over'>😞 Sorry, Computer Won the Game. 😞</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='scoreboard'>Final Score: <strong>You {st.session_state.player_score}</strong> - <strong>Computer {st.session_state.computer_score}</strong></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Play Again'):
            reset_game()
    with col2:
        if st.button('Quit'):
            st.session_state.game_state = 'menu'
            reset_game()
