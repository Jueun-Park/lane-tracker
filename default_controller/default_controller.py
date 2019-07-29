import os
import argparse
import gym
import donkey_gym
import time
import random
import numpy as np

import cv2
from simple_pid import PID
from lane_detector import LaneDetector

NUM_EPISODES = 1
MAX_TIME_STEPS = 10000000

# TODO: hyperparameters
steer_controller = PID(Kp=3.0,
                Ki=0.0,
                Kd=0.175,
                output_limits=(-1, 1),
                )
base_speed = 1
speed_controller = PID(Kp=1.0,
                Ki=0.0,
                Kd=0.125,
                output_limits=(-1, 1),
                )

def simulate(env):
    detector = LaneDetector()
    for episode in range(NUM_EPISODES):
        obv = env.reset()  # TODO: reset delay
        obv = cv2.cvtColor(obv, cv2.COLOR_RGB2BGR)
        steer = 0

        for t in range(MAX_TIME_STEPS):
            is_okay, angle_error = detector.detect_lane(obv)
            angle_error = -angle_error
            if not detector.left:
                # print(str(time.time()) + " no left")
                pass
            elif not detector.right:
                # print(str(time.time()) + " no right")
                pass

            steer = steer_controller(angle_error)
            print(time.time(), "steer:", steer)
            reduction = speed_controller(steer)
            speed = base_speed - np.abs(reduction)

            action = (steer, speed)
            obv, reward, done, _ = env.step(action)
            
            obv = cv2.cvtColor(obv, cv2.COLOR_RGB2BGR)
            cv2.imshow('input', detector.original_image_array)
            if done:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":

    # Initialize the donkey environment
    # where env_name one of:
    env_list = [
        "donkey-warehouse-v0",
        "donkey-generated-roads-v0",
        "donkey-avc-sparkfun-v0",
        "donkey-generated-track-v0"
    ]

    parser = argparse.ArgumentParser(description='gym_test')
    parser.add_argument('--sim', type=str, default="sim_path",
                        help='path to unity simulator. maybe be left at default if you would like to start the sim on your own.')
    parser.add_argument('--headless', type=int, default=0,
                        help='1 to supress graphics')
    parser.add_argument('--port', type=int, default=9091,
                        help='port to use for websockets')
    parser.add_argument('--env_name', type=str, default='donkey-generated-track-v0',
                        help='name of donkey sim environment', choices=env_list)

    args = parser.parse_args()

    #we pass arguments to the donkey_gym init via these
    os.environ['DONKEY_SIM_PATH'] = args.sim
    os.environ['DONKEY_SIM_PORT'] = str(args.port)
    os.environ['DONKEY_SIM_HEADLESS'] = str(args.headless)

    env = gym.make(args.env_name)

    simulate(env)

    env.close()

    print("test finished")
