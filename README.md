# Backgammon Classic Reinforcement Learning
Solving backgammon using classical reinforcement learning techniques

## Status

I've currently just copied the example file from the gym and tried to make sense of it. I've also realized that I need to understand backgammon first in order to make sense of the "available_actions" parameter. The file is named ```play_random_agents.py``

## Gym

We are using the https://github.com/dellalibera/gym-backgammon gym for training the reinforcement learning model

### Installation

If there are no pip environments - create one by issuing the following command
> virtualenv env

Then activate the virtual environment
> source env/bin/activate


Clone the following github repository, containing the gym
> git clone https://github.com/dellalibera/gym-backgammon.git

Change directory into the gym, and pip install the gym by issuing the following command
> cd gym-backgammon/ && pip install -e .

Or just run the install script by doing the following steps

1. First make the file executable by issuing the following command
    - >chmod +x install_environment.sh
2. If you do not have virtualenv installed, then install it for your distro. It can be installed in Ubuntu by issuing the following command
    - >sudo apt install python-virtualenv
3. Then run the script
    - >./install_environment.sh

## Interesting Links

[Temporal Difference Learning and TD-Gammon](https://cling.csd.uwo.ca/cs346a/extra/tdgammon.pdf)

[Deep reinforcement learning compared with Q-table learning applied to backgammon](https://www.kth.se/social/files/58865ec8f27654607fb6e9a4/PFinnman_MWinberg_dkand16.pdf)

[Gym Environment](https://github.com/dellalibera/gym-backgammon.git)