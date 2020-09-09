# SUMO-OpenAI-GYM-Environment


This is a Simulation of Urban Mobility (SUMO) OpenAI Gym compatible environment for usage in reinforcement learning training. We created our own custom environment then wrapped it using OpenAI GYM's specification.
You will need to implement your own state definition and reward functions depending on your Agent's Observation Input.

This was originally developed for custom usage within our own custom solution at https://www.citix.ai but we later on decided to open it up for others to benefit from.
Feel free to use this project however you see fit.

Notes:

Please check the internal Model Parameters under Sumo_Environment.py and make sure it fits your agent implementation. For Any questions, don't hesitate to reach out.


Originally tested with PFRL and SUMO 1.6.0



## Prerequsites:

1) Please make sure you have SUMO installed and your path variables setup correctly.
2) Please make sure you have OpenAI's GYM toolkit installed
