# DeepCollision Algorithm

## Network Architecture
we used a four-layer fully connected DNN with the following architecture: **an input layer with 12 neurons** corresponding to the 12 state parameters, **one output layer with 52 neurons** corresponding to the 52 environment configuration actions, and **2 hidden layers with 200 neurons each**. For these two hidden layers, the Rectified Linear Unit (ReLU) activation was applied to their neurons to accelerate the convergence of the network parameter optimization.
## Pseudocode
<div align=center><img src="https://github.com/simplexity-lab/DeepCollision/blob/main/algorithms/figures/dqn-based_environment_configuration.png"  width="600" /></div>

## Hyperparameter settings
<div align=center><img src="https://github.com/simplexity-lab/DeepCollision/blob/main/algorithms/figures/hyperparameter_settings.png"  zoom="10%" /></div>
