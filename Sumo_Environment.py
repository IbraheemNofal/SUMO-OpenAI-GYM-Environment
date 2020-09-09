

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import json
import math
import numpy as np
from pathlib import Path
import re
import gym
from gym import spaces
from gym import error, spaces, utils
from gym.utils import seeding
import threading
import time

from TLS_Manager import TLS_Manager



# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci




class SUMO_Environment(gym.Env):

    #set model parameters

    Agent_Type = "dueling_dqn"


    num_states = 4
    num_actions = 4  #4 TLS phases
    
    state_shape = (93)
    Num_Of_Timesteps_Used_In_Observation = 2

    min_Phase_Length = 0 #the minimum length for a phase in sumo steps
    Yellow_Phase_Length = 3 #the length of the yellow phase
    Agent_Step_Interval = 1 #we'll be calling the run method inside runner once every this much simulation interations, this counts as one STEP as far as the DQN model is concerned
    max_episode_timesteps = int(3000 / Agent_Step_Interval)
    prep_time = 20 # the time given before the agent starts getting rewards for its actions
    render_bool = False

    TLS_ID = "gneJ79" #make sure this TLS ID matches the one in your sumo net file

    current_episode = 1 #the current training episode

    TLS_Manager = None #store reference to TLS manager


    def __init__(self, test):
        
        super(SUMO_Environment,self).__init__()
      
        #whether this is a test environment or not
        self.test = test
        #whether to run SUMO in GUI mode or not
        self.name = "SUMO"

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(self.num_actions)
        # The observation will be the coordinate of the agent
        # this can be described both by Discrete and Box space
        self.observation_space = spaces.Box(low=-2000, high = 72000,
                                            shape=(self.state_shape, self.Num_Of_Timesteps_Used_In_Observation), dtype=np.float32)
        #self.initialize_simulation()

    def initialize_simulation(self):
        

        print("\n\nStarting episode #"+str(self.current_episode-1))
        print("\n\n")


        #clear managers array
        self.TLS_Manager = None
        
        self.number_of_Steps_taken_by_agent = 0

        if self.render_bool:
            __Restart__("")
        else:
            __Restart__("--nogui")

        
        #instantiate TLS managers
        self.TLS_Manager = TLS_Manager(self.TLS_ID,self.state_shape,self.Num_Of_Timesteps_Used_In_Observation)
        
        


    def step(self, action):
        
        #print("taking a step")

        observation = np.zeros(shape = (self.Num_Of_Timesteps_Used_In_Observation, self.state_shape))
        observation = np.moveaxis(observation, 0, -1)

        Reward = 0

        Terminal = False

        Info = dict()



        #increment step counter
        self.number_of_Steps_taken_by_agent += 1


        #take step

    

        Sumo_Expected_Vehicles = traci.simulation.getMinExpectedNumber()




    
        
        #check if action results in phase change, if so set to yellow
        phase_changed = False

        #check if a phase change occurred so we can later switch to yellow if required
        if self.TLS_Manager.get_Phase() != action:
            #phase changed
            phase_changed = True
            #set to yellow
            self.TLS_Manager.set_Phase_To_Yellow()
        

        #progress simulation by one step
        if not phase_changed:

            traci.simulationStep()
            #inrement phase length counter
            self.TLS_Manager.time_Elapsed_In_Current_Phase += 1

            #update queues
            self.TLS_Manager.update_TLS_Queues()


        #update TLS Qeues when in yellow, and run simulation steps equal to yellow phase length
        while phase_changed and self.TLS_Manager.time_Elapsed_In_Current_Phase <= self.Yellow_Phase_Length:
        
            if self.TLS_Manager.time_Elapsed_In_Current_Phase == self.Yellow_Phase_Length:
                #yellow phase should end, take action
                self.TLS_Manager.Execute_Action(action)
                phase_changed = False

            traci.simulationStep()
            #inrement phase length counter
            self.TLS_Manager.time_Elapsed_In_Current_Phase += 1


            #update queues
            self.TLS_Manager.update_TLS_Queues()



        #pass observations and take actions

        #let agent know when it reaches terminal state
        if Sumo_Expected_Vehicles == 0 or self.number_of_Steps_taken_by_agent == self.max_episode_timesteps:
            #terminal when we reach max number of steps or no vehicles are left in simulation
            Terminal = True
            self.TLS_Manager.terminal_state = True

        #Get TLS state representation this timestep
        observation = self.TLS_Manager.Get_State()

        #reward is zero when we're in prep_time
        if self.TLS_Manager.step > self.prep_time:
            Reward = self.TLS_Manager.Evaluate_Reward()


        return observation, Reward, Terminal, Info

            

    def reset(self):
        #reset simulation
        try:
            traci.close()

        except traci.exceptions.FatalTraCIError:
            print("An error occurred when trying to close traci connection")

        self.current_episode += 1

        #initialize simulation and start SUMO client
        self.initialize_simulation()

        self.TLS_Manager = None #index in TLS_Managers_Array
        self.number_of_Steps_taken_by_agent = 0


        observation = self.TLS_Manager.Get_State()

        return observation  # reward, done, info can't be included               


    def render(self, mode='human'):
        #set gui variable to true
        self.render_bool = True
        print("rendering")


    def close(self):
        #close sumo simulation
        
        traci.close()
           



    
def __Restart__(options):


    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options == "--nogui":
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')


    # first, if necessary, generate the route file for this simulation
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "/home/ibraheem/Desktop/Traffic-Management-System/Road Network/cross.sumocfg",
                                "--tripinfo-output", "tripinfo.xml","--time-to-teleport","-100", "--quit-on-end"]) #time to teleport value is set to -100 in order to turn off teleporting

