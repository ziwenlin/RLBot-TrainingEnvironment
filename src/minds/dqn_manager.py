import random
from collections import deque
from typing import Dict

import numpy as np
import tensorflow as tf

from minds.util.neural_helpers import convert_game_state_to_6x3_state, convert_game_state_to_3x3_state

tf.get_logger().setLevel('INFO')
from keras import Sequential, Input
from keras.layers import Conv2D, Activation, MaxPooling2D, Dropout, Flatten, Dense
from keras.optimizer_v2.adam import Adam
from rlbot.agents.base_agent import SimpleControllerState

from util.agent_base import BaseTrainingAgent

DISCOUNT = 0.99
REPLAY_MEMORY_SIZE = 50_000  # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 1_000  # Minimum number of steps in a memory to start training
MINIBATCH_SIZE = 64  # How many steps (samples) to use for training
UPDATE_TARGET_EVERY = 5  # Terminal states (end of episodes)
MODEL_NAME = '2x256'
MIN_REWARD = -200  # For model save
MEMORY_FRACTION = 0.20

# Environment settings
EPISODES = 20_000

# Exploration settings
epsilon = 1  # not a constant, going to be decayed
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

#  Stats settings
AGGREGATE_STATS_EVERY = 50  # episodes
SHOW_PREVIEW = False

ACTION_SPACE_SIZE = 11
ACTION_SPACE_ROLL = 7

class Environment:
    OBSERVATION_SPACE_VALUES = (3, 3)
    ACTION_SPACE_SIZE = 11
    ACTION_THROTTLE = [1 - (i * 2) / (ACTION_SPACE_SIZE - 1) for i in range(ACTION_SPACE_SIZE)]
    ACTION_STEER = [1 - (i * 2) / (ACTION_SPACE_SIZE - 1) for i in range(ACTION_SPACE_SIZE)]
    ACTION_SPACE_ROLL = 7
    ACTION_ROLL = [1 - (i * 2) / (ACTION_SPACE_ROLL - 1) for i in range(ACTION_SPACE_ROLL)]


env = Environment()


class DQNManager:
    def __init__(self, agent: BaseTrainingAgent):
        self.agents: Dict[str, DQNAgent] = {}
        self.manager = agent
        self.epsilon = 1

        self.previous_state = self.get_current_state()
        self.previous_action = np.random.randint(0, env.ACTION_SPACE_SIZE)

        self.is_first_step = True
        self.is_setup = True
        self.is_done = False
        self.is_ready = False
        self.step = 1
        self.episode = 0

    def create_agents(self):
        agent = self.manager
        self.agents: Dict[str, DQNAgent] = {
            a: DQNAgent(agent) for a in ['throttle', 'steer', ]#'actions']
        }
        self.is_ready = True

    def step_action(self, action):
        throttle = pitch = env.ACTION_THROTTLE[action[0]]
        steer = yaw = env.ACTION_STEER[action[1]]
        if 'Action' in self.agents:
            roll = env.ACTION_ROLL[action[2]] if action[2] < env.ACTION_SPACE_ROLL else 0
            jump, boost, handbrake, rumble = [a == action[2] for a in range(env.ACTION_SPACE_ROLL, env.ACTION_SPACE_SIZE)]
        else:
            roll = 0
            jump, boost, handbrake, rumble = [False] * 4
        controller = SimpleControllerState()
        controller.throttle = throttle
        controller.steer = steer
        controller.boost = boost
        controller.jump = jump
        controller.pitch = pitch
        controller.yaw = yaw
        controller.roll = roll
        controller.handbrake = handbrake
        controller.use_item = rumble
        self.manager.agent_controller = controller

    def get_current_state(self):
        game_state = self.manager.game_state
        game_state_items = self.manager.game_items
        return np.array(convert_game_state_to_3x3_state(game_state, game_state_items))

    def get_actions(self, current_state):
        return [np.argmax(agent.get_qs(current_state)) for agent in self.agents.values()]

    def step_get(self):
        current_state = self.get_current_state()
        done = self.manager.training.episode_index != self.episode
        try:
            reward = self.manager.training.episode.data[self.episode]['reward']
        except:
            reward = -2
        return current_state, reward, done

    def step_setup(self):
        if not self.is_setup:
            return
        self.step = 1
        self.episode = self.manager.training.episode_index
        self.is_first_step = True
        # self.previous_state = self.manager.game_state

    def step_end(self, done):
        if self.manager.training.episode_index == self.episode:
            return
        self.is_done = False
        self.is_setup = True
        if self.epsilon > MIN_EPSILON:
            self.epsilon *= EPSILON_DECAY
            self.epsilon = max(MIN_EPSILON, self.epsilon)

    def step_training(self):
        if not self.is_ready:
            return
        if not self.manager.training.is_running:
            return
        self.step_setup()
        current_state, reward, done = self.step_get()
        if self.is_done:
            self.step_end(done)
            for agent in self.agents.values():
                agent.edit_last_replay(reward)
            return

        if np.random.random() > self.epsilon:
            actions = self.get_actions(current_state)
        else:
            actions = [np.random.randint(0, env.ACTION_SPACE_SIZE)
                       for _ in range(len(self.agents))]

        self.step_action(actions)

        if self.is_first_step:
            # The agent got teleported which means previous state is
            # way too different than current state
            replay_step = self.previous_state, self.previous_action, reward, current_state, done
            for index, agent in enumerate(self.agents.values()):
                agent.update_replay_memory(replay_step)
            self.is_first_step = False
        # We don't want to train here because it is cpu expensive
        # self.agent.train(done, self.step)

        self.previous_state = current_state
        self.previous_action = actions
        self.is_done = done

    def step_normal(self):
        if not self.is_ready:
            return
        self.previous_state = current_state = self.get_current_state()
        self.previous_action = action = self.get_actions(current_state)
        self.step_action(action)


# Agent class
class DQNAgent:
    def __init__(self, agent):
        self.agent = agent

        # Main model
        self.model = self.create_model()

        # Target network
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps for training
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = lambda *_: None
        # self.tensorboard = ModifiedTensorBoard(log_dir="logs/{}-{}".format(MODEL_NAME, int(time.time())))

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0

    def create_model(self):
        model = Sequential()

        # OBSERVATION_SPACE_VALUES = (3, 4, 3) a 3x4 XYZ data.
        # model.add(Conv2D(256, (1, 2), input_shape=env.OBSERVATION_SPACE_VALUES))
        # model.add(Activation('relu'))
        # model.add(MaxPooling2D(pool_size=(2, 2)))
        # model.add(Dropout(0.2))
        #
        # model.add(Conv2D(256, 1))
        # model.add(Activation('relu'))
        # model.add(MaxPooling2D(pool_size=(1, 1)))
        # model.add(Dropout(0.2))

        # this converts our 3D feature maps to 1D feature vectors
        model.add(Flatten(input_shape=env.OBSERVATION_SPACE_VALUES))
        model.add(Dense(32))
        model.add(Dense(32))

        model.add(Dense(env.ACTION_SPACE_SIZE, activation='relu'))  # ACTION_SPACE_SIZE = how many choices (9)
        model.compile(loss="mse", optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

        # model._make_predict_function()
        # model._make_test_function()
        # model._make_train_function()

        return model

    # Adds step's data to a memory replay array
    # (observation space, action, reward, new observation space, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def edit_last_replay(self, reward):
        if len(self.replay_memory) == 0:
            return
        replay_step = self.replay_memory.pop()
        replay_step = replay_step[:2] + tuple([reward]) + replay_step[3:]
        self.replay_memory.append(replay_step)

    # Queries main network for Q values given current observation space (environment state)
    def get_qs(self, state):
        state = np.array(state).reshape(-1, *state.shape)
        return self.model.predict(state)[0]

    def train(self, terminal_state, step, action_index):
        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)
        X, y = [], []
        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action[action_index]] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)

            # Fit on all samples as one batch, log only on terminal state
            # self.model.fit(np.array(X), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False)
            # self.model.fit(np.array(X), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False,
            #                callbacks=[self.tensorboard] if terminal_state else None)

            # Update target network counter every episode
            if terminal_state:
                self.target_update_counter += 1

            # If counter reaches set value, update target network with weights of main network
            if self.target_update_counter > UPDATE_TARGET_EVERY:
                self.target_model.set_weights(self.model.get_weights())
                self.target_update_counter = 0


if __name__ == '__main__':
    test = DQNManager(BaseTrainingAgent())
