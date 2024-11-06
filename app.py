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
    thumb_is_open = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
    fingers_open = [
        hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y
        for tip in [8, 12, 16, 20]
    ]
    open_count = sum(fingers_open)
    if open_count == 2 and not thumb_is_open:
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
st.markdown("""
    <style>
    .title {
        text-align: center;
        color: #FF6347;
        font-size: 50px;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        font-size: 24px;
        color: #FFFFFF;
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
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='title'>Rock Paper Scissors</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Play against the computer using your webcam!</div>", unsafe_allow_html=True)

if st.session_state.game_state == 'menu':
    st.markdown("<div class='button'><button class='btn' onclick='window.location.reload();'>Start Game</button></div>", unsafe_allow_html=True)
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
    st.write('Show your hand gesture for Rock ✊, Paper ✋, or Scissors ✌️!')
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
                elif (player_choice == 'Rock' and computer_choice == 'Scissors') or \
                     (player_choice == 'Paper' and computer_choice == 'Rock') or \
                     (player_choice == 'Scissors' and computer_choice == 'Paper'):
                    result = "You win this round!"
                    st.session_state.player_score += 1
                else:
                    result = "Computer wins this round!"
                    st.session_state.computer_score += 1

                st.session_state.player_choice = player_choice
                st.session_state.computer_choice = computer_choice
                st.session_state.last_result = result
                st.image(frame_rgb, caption='Your Move', use_column_width=True)

                st.markdown(f"<div class='scoreboard'><strong>You chose:</strong> {player_choice} | <strong>Computer chose:</strong> {computer_choice}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='scoreboard'>Score: <strong>You {st.session_state.player_score}</strong> - <strong>Computer {st.session_state.computer_score}</strong></div>", unsafe_allow_html=True)

                st.session_state.round_number += 1
                if st.session_state.player_score >= st.session_state.winning_score or st.session_state.computer_score >= st.session_state.winning_score:
                    st.session_state.game_state = 'game_over'
                else:
                    if st.button('Next Round'):
                        st.session_state.game_state = 'countdown'
                        st.session_state.countdown = 3
                        st.session_state.countdown_active = True
                        st.session_state.timer_start = time.time()
            else:
                st.write('Could not recognize your gesture. Please try again.')
                st.image(frame_rgb, caption='Your Move', use_column_width=True)

else:
    if st.session_state.player_score > st.session_state.computer_score:
        st.markdown("<div class='game-over'>🎉 Congratulations, You Won the Game! 🎉</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='game-over'>😞 Sorry, Computer Won the Game. 😞</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='scoreboard'>Final Score: <strong>You {st.session_state.player_score}</strong> - <strong>Computer {st.session_state.computer_score}</strong></div>", unsafe_allow_html=True)
    if st.button('Play Again'):
        reset_game()
