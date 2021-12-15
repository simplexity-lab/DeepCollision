# Public Data for Peer Review of DeepCollision

> To facilitate reviewing our proposed approach, reviewers please refer to the corresponding data in this repository:<br/>
> **[algorithms](https://github.com/simplexity-lab/DeepCollision/tree/main/algorithms)**, pseudocode for DeepCollision and Hyper-parameters of DQN in DeepCollision;<br/>
> **[formal-experiment](https://github.com/simplexity-lab/DeepCollision/tree/main/formal-experiment)**, all data and plots for the formal experiment;<br/> 
> **[pilot-study](https://github.com/simplexity-lab/DeepCollision/tree/main/pilot-study)**, all data and plots for the pilot study;<br/> 
> **[rest-api](https://github.com/simplexity-lab/DeepCollision/tree/main/rest-api)**, one example and all implemented REST APIs for environment parameter configurations.

## Overview of DeepCollision

**DeepCollision** learns environment configurations to maximize collisions of an Autonomous Vehicle Under Test (AVUT). As shown in the following figure, DeepCollision employs a *Simulator* (e.g., LGSVL) to simulate the *Testing Environment* comprising the AVUT and its operating environment. DeepCollision also integrates with an *Autopilot Algorithm Platform* (e.g., the Baidu Apollo ) deployed on the AVUT to enable its autonomous driving.

<div align=center><img src="https://github.com/simplexity-lab/DeepCollision/blob/main/figures/Overview.png" style="zoom:20%" /></div>

**DeepCollision** employs a DQN component to generate a set of actions to configure the environment of the AVUT, e.g., weather condition, time of day. At each time step t, the DQN component observes a state S<sub>t</sub> describing the current states of the AVUT and its environment. With the state, DeepCollision decides an action A<sub>t</sub> based on the Q-network with the policy <a href="https://www.codecogs.com/eqnedit.php?latex=\pi" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\pi" title="\pi" /></a>. With our developed *Environment Configuration REST API*, such an action A<sub>t</sub> can be considered as an HTTP request for accessing the simulator to introduce new environment configurations. 

After the AVUT driving into a new environment within a fixed time period, both the AVUT and its environment will enter a new state S<sub>t+1</sub>. Based on the observed states of the AVUT and its environment, *Reward calculator* calculates a reward R<sub>t</sub> for A<sub>t</sub> and S<sub>t</sub> at t+1. Then DQN stores them (as S<sub>t</sub>, A<sub>t</sub>, R<sub>t</sub>, S<sub>t+1</sub>) into the replay memory buffer.

Once the replay memory is full, Q-network will be updated based on the loss function by a mini-batch randomly selected from the updated replay memory. In addition, with S<sub>t+1</sub>, the (updated) Q-network with policy <a href="https://www.codecogs.com/eqnedit.php?latex=\pi" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\pi" title="\pi" /></a> decides the next action: A<sub>t+1</sub>. In DeepCollision, an episode is finished once the AVUT arrives at its destination or the AVUT cannot move for a specific duration. 

At each time step t, the information about the AVUT (e.g., its driving and collision status) and its environment (e.g., its status and driving scenarios) are stored as *Environment Configuration Logs* for further analyses and collision replaying. 

More details of Hyper-parameters of DQN used in DeepCollision can be accessed here [Hyper-parameters](https://github.com/DeepCollision/DeepCollisionData/blob/main/DeepCollison%20Algorithm/Hyper-parameters.md).
