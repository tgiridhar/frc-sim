import random
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def simulate_match(params):
    """
    Simulates a match of REEFSCAPE second-by-second based on input parameters and task durations.
    :param params: A dictionary containing success probabilities and scoring opportunities for tasks.
    :return: A timeline of actions for each alliance and their scores.
    """
    def attempt_task(success_prob):
        """Simulates a single task attempt based on success probability."""
        return random.random() < success_prob

    def pick_task_duration(min_time, max_time):
        """Returns a random task duration within the given range."""
        return random.randint(min_time, max_time)

    timeline = []
    red_alliance = {"score": 0, "actions": [[], [], []]}  # Actions for 3 robots
    blue_alliance = {"score": 0, "actions": [[], [], []]}  # Actions for 3 robots
    net_fill_red = 0
    net_fill_blue = 0
    red_tasks = [0, 0, 0]  # Tracks task completion times for each red robot
    blue_tasks = [0, 0, 0]  # Tracks task completion times for each blue robot

    # Simulate the match second by second
    for second in range(1, 151):  # 2:30 minutes = 150 seconds
        red_robot_actions = ["", "", ""]
        blue_robot_actions = ["", "", ""]

        # Red Alliance actions
        for robot_idx in range(3):
            if red_tasks[robot_idx] <= second:  # Robot is available
                if second <= 15:  # Autonomous period
                    if attempt_task(params['red']['auto_leave_prob']):
                        red_robot_actions[robot_idx] = "Leaves start line"
                        red_alliance['score'] += 3
                        red_tasks[robot_idx] = second + pick_task_duration(1, 2)
                    elif attempt_task(params['red']['auto_coral_l1_prob']):
                        red_robot_actions[robot_idx] = "Scores coral on L1"
                        red_alliance['score'] += 3
                        red_tasks[robot_idx] = second + pick_task_duration(3, 5)
                    elif attempt_task(params['red']['auto_algae_processor_prob']):
                        red_robot_actions[robot_idx] = "Drops algae in processor"
                        red_alliance['score'] += 6
                        red_tasks[robot_idx] = second + pick_task_duration(5, 7)
                else:  # Teleop period
                    if second % 5 == 0 and attempt_task(params['red']['teleop_algae_processor_prob']):
                        red_robot_actions[robot_idx] = "Drops algae in processor"
                        red_alliance['score'] += 6
                        red_tasks[robot_idx] = second + pick_task_duration(5, 10)
                    elif second % 7 == 0 and attempt_task(max(0.1, params['red']['teleop_algae_net_prob'] - 0.05 * net_fill_red)):
                        red_robot_actions[robot_idx] = "Shoots algae into net"
                        red_alliance['score'] += 4
                        net_fill_red += 1
                        red_tasks[robot_idx] = second + pick_task_duration(7, 12)
                    elif second % 10 == 0 and attempt_task(params['red']['teleop_coral_l3_prob']):
                        red_robot_actions[robot_idx] = "Scores coral on L3"
                        red_alliance['score'] += 4
                        red_tasks[robot_idx] = second + pick_task_duration(5, 8)

        # Blue Alliance actions
        for robot_idx in range(3):
            if blue_tasks[robot_idx] <= second:  # Robot is available
                if second <= 15:  # Autonomous period
                    if attempt_task(params['blue']['auto_leave_prob']):
                        blue_robot_actions[robot_idx] = "Leaves start line"
                        blue_alliance['score'] += 3
                        blue_tasks[robot_idx] = second + pick_task_duration(1, 2)
                    elif attempt_task(params['blue']['auto_coral_l1_prob']):
                        blue_robot_actions[robot_idx] = "Scores coral on L1"
                        blue_alliance['score'] += 3
                        blue_tasks[robot_idx] = second + pick_task_duration(3, 5)
                    elif attempt_task(params['blue']['auto_algae_processor_prob']):
                        blue_robot_actions[robot_idx] = "Drops algae in processor"
                        blue_alliance['score'] += 6
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 7)
                else:  # Teleop period
                    if second % 5 == 0 and attempt_task(params['blue']['teleop_algae_processor_prob']):
                        blue_robot_actions[robot_idx] = "Drops algae in processor"
                        blue_alliance['score'] += 6
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 10)
                    elif second % 7 == 0 and attempt_task(max(0.1, params['blue']['teleop_algae_net_prob'] - 0.05 * net_fill_blue)):
                        blue_robot_actions[robot_idx] = "Shoots algae into net"
                        blue_alliance['score'] += 4
                        net_fill_blue += 1
                        blue_tasks[robot_idx] = second + pick_task_duration(7, 12)
                    elif second % 10 == 0 and attempt_task(params['blue']['teleop_coral_l3_prob']):
                        blue_robot_actions[robot_idx] = "Scores coral on L3"
                        blue_alliance['score'] += 4
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 8)

        # Record timeline
        timeline.append({
            "second": second,
            "red_actions": red_robot_actions,
            "blue_actions": blue_robot_actions,
            "red_score": red_alliance['score'],
            "blue_score": blue_alliance['score']
        })

    return timeline

def plot_scoreboard(timeline):
    """Plots the scoreboard and actions over time."""
    seconds = [event['second'] for event in timeline]
    red_scores = [event['red_score'] for event in timeline]
    blue_scores = [event['blue_score'] for event in timeline]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(seconds, red_scores, label="Red Alliance", color="red")
    ax.plot(seconds, blue_scores, label="Blue Alliance", color="blue")

    ax.set_title("REEFSCAPE Match Score Over Time")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Score")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Streamlit UI
st.title("REEFSCAPE Second-by-Second Match Simulator")

st.sidebar.header("Adjust Probabilities")
def get_params(alliance_name):
    return {
        "auto_leave_prob": st.sidebar.slider(f"{alliance_name} Auto Leave Probability", 0.0, 1.0, 1.0),
        "auto_coral_l1_prob": st.sidebar.slider(f"{alliance_name} Auto Coral L1 Probability", 0.0, 1.0, 0.9),
        "auto_algae_processor_prob": st.sidebar.slider(f"{alliance_name} Auto Algae Processor Probability", 0.0, 1.0, 0.8),

        "teleop_algae_processor_prob": st.sidebar.slider(f"{alliance_name} Teleop Algae Processor Probability", 0.0, 1.0, 0.8),
        "teleop_algae_net_prob": st.sidebar.slider(f"{alliance_name} Teleop Algae Net Probability", 0.0, 1.0, 0.4),
        "teleop_coral_l3_prob": st.sidebar.slider(f"{alliance_name} Teleop Coral L3 Probability", 0.0, 1.0, 0.5),
    }

parameters = {
    "red": get_params("Red Alliance"),
    "blue": get_params("Blue Alliance")
}

if st.button("Simulate Match"):
    timeline = simulate_match(parameters)
    st.subheader("Match Timeline")

    df = pd.DataFrame(timeline)
    st.write(df)

    plot_scoreboard(timeline)
