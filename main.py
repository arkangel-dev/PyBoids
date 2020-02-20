import PyBoids

env = PyBoids.Environment() # create environment
env.AddBoidArray(70) # Add 30 bords
env.AddObservingMember() # Add an observing bord
env.Start() # Start the simulation