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
    st.session_state.winning_score = 3  # Adjust winning score as desired
    st.session_state.last_result = ''
    st.session_state.player_choice = ''
    st.session_state.computer_choice = ''
    st.session_state.countdown_active = False
    st.session_state.timer_start = None

# Function to classify hand gestures
def classify_hand_gesture(hand_landmarks):
    thumb_is_open = False
    index_is_open = False
    middle_is_open = False
    ring_is_open = False
    pinky_is_open = False

    # Tip landmarks for each finger
    tip_ids = [4, 8, 12, 16, 20]

    # Thumb: compare x-coordinate because it moves horizontally
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0]-2].x:
        thumb_is_open = True

    # Other fingers: compare y-coordinate
    if hand_landmarks.landmark[tip_ids[1]].y < hand_landmarks.landmark[tip_ids[1]-2].y:
        index_is_open = True
    if hand_landmarks.landmark[tip_ids[2]].y < hand_landmarks.landmark[tip_ids[2]-2].y:
        middle_is_open = True
    if hand_landmarks.landmark[tip_ids[3]].y < hand_landmarks.landmark[tip_ids[3]-2].y:
        ring_is_open = True
    if hand_landmarks.landmark[tip_ids[4]].y < hand_landmarks.landmark[tip_ids[4]-2].y:
        pinky_is_open = True

    # Determine the gesture
    if index_is_open and middle_is_open and not ring_is_open and not pinky_is_open and not thumb_is_open:
        return 'Scissors'
    elif index_is_open and middle_is_open and ring_is_open and pinky_is_open and thumb_is_open:
        return 'Paper'
    elif not index_is_open and not middle_is_open and not ring_is_open and not pinky_is_open and not thumb_is_open:
        return 'Rock'
    else:
        return 'Unknown'

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

# Title and instructions
st.title('Rock Paper Scissors Game')
st.write('Play Rock-Paper-Scissors against the computer using your webcam!')

# Main Menu
if st.session_state.game_state == 'menu':
    if st.button('Start Game'):
        st.session_state.game_state = 'countdown'
        st.session_state.countdown_active = True
        st.session_state.timer_start = time.time()
elif st.session_state.game_state == 'countdown':
    # Countdown logic
    if st.session_state.countdown_active:
        elapsed_time = int(time.time() - st.session_state.timer_start)
        st.session_state.countdown = 3 - elapsed_time
        if st.session_state.countdown > 0:
            st.write(f'Get Ready: {st.session_state.countdown}')
        else:
            st.session_state.countdown_active = False
            st.session_state.game_state = 'playing'
    else:
        st.session_state.game_state = 'playing'
        st.session_state.player_choice = ''
        st.session_state.computer_choice = ''
        st.session_state.last_result = ''
        st.session_state.timer_start = None
elif st.session_state.game_state == 'playing':
    st.write(f'Round {st.session_state.round_number}')
    st.write('Make your move!')

    # Capture image from webcam
    img_file_buffer = st.camera_input("Show your move")

    if img_file_buffer is not None:
        # To read image file buffer with OpenCV:
        bytes_data = img_file_buffer.getvalue()
        np_arr = np.frombuffer(bytes_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75) as hands:

            # Process the image to detect hands
            results = hands.process(frame)

            player_choice = 'Unknown'

            # If hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Classify the gesture
                    player_choice = classify_hand_gesture(hand_landmarks)

                    # Draw hand landmarks on the frame
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if player_choice in ['Rock', 'Paper', 'Scissors']:
                # Computer randomly chooses a gesture
                computer_choice = random.choice(['Rock', 'Paper', 'Scissors'])

                # Determine the winner
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

                # Display the frame with landmarks
                st.image(frame, caption='Your Move', use_column_width=True)

                # Show choices and result
                st.write(f'You chose: **{player_choice}**')
                st.write(f'Computer chose: **{computer_choice}**')
                st.write(f'**{result}**')

                # Display scores
                st.write(f'Score: You {st.session_state.player_score} - Computer {st.session_state.computer_score}')

                st.session_state.round_number += 1

                # Check for game over
                if st.session_state.player_score >= st.session_state.winning_score or st.session_state.computer_score >= st.session_state.winning_score:
                    st.session_state.game_state = 'game_over'
                else:
                    # Start next round after countdown
                    if st.button('Next Round'):
                        st.session_state.game_state = 'countdown'
                        st.session_state.countdown = 3
                        st.session_state.countdown_active = True
                        st.session_state.timer_start = time.time()
            else:
                st.write('Could not recognize your gesture. Please try again.')
                # Display the frame with landmarks
                st.image(frame, caption='Your Move', use_column_width=True)
else:
    # Game Over
    if st.session_state.player_score > st.session_state.computer_score:
        st.write('## Congratulations, You Won the Game!')
    else:
        st.write('## Sorry, Computer Won the Game.')

    st.write(f'Final Score: You {st.session_state.player_score} - Computer {st.session_state.computer_score}')

    if st.button('Play Again'):
        reset_game()
