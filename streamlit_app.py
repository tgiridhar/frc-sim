import random
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from matplotlib.animation import FuncAnimation

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

    def random_location(zone):
        """Generates a random (x, y) location within a specified zone."""
        x_min, x_max, y_min, y_max = zone
        return random.uniform(x_min, x_max), random.uniform(y_min, y_max)

    # Define zones for each alliance
    red_zones = {
        "coral": (0, 3, 0, 3),
        "processor": (7, 10, 7, 10),
        "barge": (4, 6, 4, 6)
    }
    blue_zones = {
        "coral": (7, 10, 0, 3),
        "processor": (0, 3, 7, 10),
        "barge": (4, 6, 4, 6)
    }

    timeline = []
    red_alliance = {"score": 0, "actions": [[], [], []], "locations": [random_location(red_zones['coral']), random_location(red_zones['coral']), random_location(red_zones['coral'])]}
    blue_alliance = {"score": 0, "actions": [[], [], []], "locations": [random_location(blue_zones['coral']), random_location(blue_zones['coral']), random_location(blue_zones['coral'])]}
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
                        red_alliance['locations'][robot_idx] = random_location(red_zones['coral'])
                    elif attempt_task(params['red']['auto_coral_l1_prob']):
                        red_robot_actions[robot_idx] = "Scores coral on L1"
                        red_alliance['score'] += 3
                        red_tasks[robot_idx] = second + pick_task_duration(3, 5)
                        red_alliance['locations'][robot_idx] = random_location(red_zones['coral'])
                    elif attempt_task(params['red']['auto_algae_processor_prob']):
                        red_robot_actions[robot_idx] = "Drops algae in processor"
                        red_alliance['score'] += 6
                        red_tasks[robot_idx] = second + pick_task_duration(5, 7)
                        red_alliance['locations'][robot_idx] = random_location(red_zones['processor'])
                else:  # Teleop period
                    if second % 5 == 0 and attempt_task(params['red']['teleop_algae_processor_prob']):
                        red_robot_actions[robot_idx] = "Drops algae in processor"
                        red_alliance['score'] += 6
                        red_tasks[robot_idx] = second + pick_task_duration(5, 10)
                        red_alliance['locations'][robot_idx] = random_location(red_zones['processor'])
                    elif second % 7 == 0 and attempt_task(max(0.1, params['red']['teleop_algae_net_prob'] - 0.05 * net_fill_red)):
                        red_robot_actions[robot_idx] = "Shoots algae into net"
                        red_alliance['score'] += 4
                        net_fill_red += 1
                        red_tasks[robot_idx] = second + pick_task_duration(7, 12)
                        red_alliance['locations'][robot_idx] = random_location(red_zones['barge'])
                    elif second % 10 == 0 and attempt_task(params['red']['teleop_coral_l3_prob']):
                        red_robot_actions[robot_idx] = "Scores coral on L3"
                        red_alliance['score'] += 4
                        red_tasks[robot_idx] = second + pick_task_duration(5, 8)
                        red_alliance['locations'][robot_idx] = random_location(red_zones['coral'])

        # Blue Alliance actions
        for robot_idx in range(3):
            if blue_tasks[robot_idx] <= second:  # Robot is available
                if second <= 15:  # Autonomous period
                    if attempt_task(params['blue']['auto_leave_prob']):
                        blue_robot_actions[robot_idx] = "Leaves start line"
                        blue_alliance['score'] += 3
                        blue_tasks[robot_idx] = second + pick_task_duration(1, 2)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['coral'])
                    elif attempt_task(params['blue']['auto_coral_l1_prob']):
                        blue_robot_actions[robot_idx] = "Scores coral on L1"
                        blue_alliance['score'] += 3
                        blue_tasks[robot_idx] = second + pick_task_duration(3, 5)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['coral'])
                    elif attempt_task(params['blue']['auto_algae_processor_prob']):
                        blue_robot_actions[robot_idx] = "Drops algae in processor"
                        blue_alliance['score'] += 6
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 7)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['processor'])
                else:  # Teleop period
                    if second % 5 == 0 and attempt_task(params['blue']['teleop_algae_processor_prob']):
                        blue_robot_actions[robot_idx] = "Drops algae in processor"
                        blue_alliance['score'] += 6
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 10)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['processor'])
                    elif second % 7 == 0 and attempt_task(max(0.1, params['blue']['teleop_algae_net_prob'] - 0.05 * net_fill_blue)):
                        blue_robot_actions[robot_idx] = "Shoots algae into net"
                        blue_alliance['score'] += 4
                        net_fill_blue += 1
                        blue_tasks[robot_idx] = second + pick_task_duration(7, 12)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['barge'])
                    elif second % 10 == 0 and attempt_task(params['blue']['teleop_coral_l3_prob']):
                        blue_robot_actions[robot_idx] = "Scores coral on L3"
                        blue_alliance['score'] += 4
                        blue_tasks[robot_idx] = second + pick_task_duration(5, 8)
                        blue_alliance['locations'][robot_idx] = random_location(blue_zones['coral'])

        # Record timeline
        timeline.append({
            "second": second,
            "red_actions": red_robot_actions,
            "blue_actions": blue_robot_actions,
            "red_score": red_alliance['score'],
            "blue_score": blue_alliance['score'],
            "red_locations": red_alliance['locations'][:],
            "blue_locations": blue_alliance['locations'][:]
        })

    return timeline

def plot_arena_with_subplots(timeline, current_second):
    """Plots the arena for both alliances as separate subplots."""
    event = timeline[current_second - 1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"REEFSCAPE Arena at Second {current_second}")

    # Red Alliance plot
    ax_red = axes[0]
    ax_red.set_xlim(0, 10)
    ax_red.set_ylim(0, 10)
    ax_red.set_title("Red Alliance")
    ax_red.set_xlabel("X-axis (field width)")
    ax_red.set_ylabel("Y-axis (field length)")
    ax_red.add_patch(plt.Rectangle((0, 0), 3, 3, color="green", alpha=0.3, label="Red Coral Area"))
    ax_red.add_patch(plt.Rectangle((7, 7), 3, 3, color="blue", alpha=0.3, label="Red Processor Area"))
    ax_red.add_patch(plt.Rectangle((4, 4), 2, 2, color="orange", alpha=0.3, label="Barge"))
    red_x, red_y = zip(*event['red_locations'])
    ax_red.scatter(red_x, red_y, color="red", label="Red Robots")
    for i, (x, y) in enumerate(event['red_locations']):
        ax_red.text(x, y, event['red_actions'][i], color="red", fontsize=8)
    ax_red.legend()

    # Blue Alliance plot
    ax_blue = axes[1]
    ax_blue.set_xlim(0, 10)
    ax_blue.set_ylim(0, 10)
    ax_blue.set_title("Blue Alliance")
    ax_blue.set_xlabel("X-axis (field width)")
    ax_blue.set_ylabel("Y-axis (field length)")
    ax_blue.add_patch(plt.Rectangle((7, 0), 3, 3, color="green", alpha=0.3, label="Blue Coral Area"))
    ax_blue.add_patch(plt.Rectangle((0, 7), 3, 3, color="blue", alpha=0.3, label="Blue Processor Area"))
    ax_blue.add_patch(plt.Rectangle((4, 4), 2, 2, color="orange", alpha=0.3, label="Barge"))
    blue_x, blue_y = zip(*event['blue_locations'])
    ax_blue.scatter(blue_x, blue_y, color="blue", label="Blue Robots")
    for i, (x, y) in enumerate(event['blue_locations']):
        ax_blue.text(x, y, event['blue_actions'][i], color="blue", fontsize=8)
    ax_blue.legend()

    st.pyplot(fig)

# Streamlit UI
st.title("REEFSCAPE Match Simulation")

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

    current_second = st.slider("Select Second to Visualize Arena", 1, 150, 1)
    plot_arena_with_subplots(timeline, current_second)

    st.subheader("Match Timeline")
    df = pd.DataFrame(timeline)
    st.write(df)
