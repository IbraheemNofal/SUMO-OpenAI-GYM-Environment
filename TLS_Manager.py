

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

import numpy as np




class TLS_Manager:

    #this class is responsible for managing the simulation, updating queues and keeping track of simulation variables


    def __init__(self, TLS_ID, state_shape,Num_Of_Timesteps_Used_In_Observation ,render=True ):

        self._stepsTaken = 0 #this variable refers to the current timestep, i.e. the steps where the agent took action and observed reward



        self.TLS_ID = TLS_ID # the ID of this traffic light system
        self.step = 0 #variable used to refer to current time inside sumo, i.e. current simulation step
        self.time_Elapsed_In_Current_Phase = 0
       

        self.Num_Of_Timesteps_Used_In_Observation = Num_Of_Timesteps_Used_In_Observation
        
        self.last_x_states = []
        self.state_shape = state_shape

        #the average time waited on this intersection for all vehicles that have previously passed by, and their counts
        self.cumulative_vehicle_count_previous_Step = 0
        self.cumulative_vehicle_avg_previous_step = 0

        #the time waited per vehicle for the first x number of vehicles in the queue on an intersection
        self.waiting_time_for_first_x_vehicles = []


        empty_state_placeholder = np.zeros(self.state_shape,dtype=float)


        i=0
        while i < self.Num_Of_Timesteps_Used_In_Observation:

            self.last_x_states.append(empty_state_placeholder)
            i += 1








    def set_Phase(self, Phase):
        #set traffic light phase

        traci.trafficlight.setPhase(self.TLS_ID,Phase)
        #reset phase time counter
        self.time_Elapsed_In_Current_Phase = 0

        self.pending_Yellow = False


    def get_Phase(self):
        #return current traffic light phase index
        x = traci.trafficlight.getPhase(self.TLS_ID)

        return x



    def get_RedYellowGreenState(self, TLS_ID):
        #get traffic light state in terms of RRRGGGYYYRRR
        return traci.trafficlight.getRedYellowGreenState(self.TLS_ID)

    def update_TLS_Queues(self):
        #THIS METHOD SHOULD BE CALLED ONCE FOR EVERY INTERSECTION AT EACH SIMULATION STEP

        #this method handles updating the vehicle Queues and internal parameters (ex: dictionaries or arrays) for your simulation, this is necessary -
        #- so that when you feed your agent observations, the queues are up to date

        #ex:
        #first retrieve data from Induction loops
        loop1 = "loop#1"
        tmp = traci.inductionloop.getLastStepVehicleIDs(loop1)

        
        TLS_GneJ80_Queue_length = 100 + tmp #a vehicle queue that's 100 vehicle long


    def set_RedYellowGreenState(self, TLS_ID, State):

        #set traffic light state in terms of RRRGGGYYYRRR
        traci.trafficlight.setRedYellowGreenState(self.TLS_ID,State)
        self.time_Elapsed_In_Current_Phase = 0

    def set_Phase_To_Yellow(self):
        #this method retrieves the current phase definition of the TLS(Traffic Light System) in terms of ex: RRRGGGRRRRRR and then masks the Green phases -
        #- and sets the currently green lights to yellow, for more info, refer to SUMO's phase definitions

        #retrieve current state
        current_RedYellowGreenState = self.get_RedYellowGreenState(self.TLS_ID)

        #mask green and set to yellow
        next_state = current_RedYellowGreenState.lower().replace("g","y")
        self.set_RedYellowGreenState(self.TLS_ID, next_state)
        self.pending_Yellow = True

    def Get_State(self):
        
        #todo: implement your own State definition here, this is what will serve as observations that are fed into the agent

        state = None
        
        return state



     
    def Append_Current_State_To_Observations(self, state):
        
        #this method appends the current state to a numpy array that also contains the last x number of states, this is useful when your current state -
        #- definition is insufficient. Ex: In the original DQN paper, they fed an agent an observation that contained the last 4 frames, so that -
        #- their observations allowed the agent to infer changes over time such as a pong ball travelling in a specific direction

        self.last_x_states.pop(0)
        #add given state to the list
        self.last_x_states.append(state)


        current_state = np.reshape(np.asfarray(self.last_x_states,dtype=np.float32),(self.Num_Of_Timesteps_Used_In_Observation,self.state_shape))
        
        #pytorch uses a channels first implementation, so we need to move axis, such that convolutions occur across the time dimension
        # current_state = np.moveaxis(current_state, 0, -1) #this may or may not be necessary, depending on whether your Reinforcement Learning framework uses channel first or channel last

        return current_state


    def Execute_Action(self, action):
      
        #set current phase
        self.set_Phase(action)





    def Evaluate_Reward(self):

        #todo: implement your own reward function here
        total_reward = -1
        return total_reward

