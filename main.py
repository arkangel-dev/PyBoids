import PyBoids

env = PyBoids.Environment((500, 500)) # create environment
env.AddObservingMember() # Add an observing bord
env.StartConsole() # Start the console
env.Start() # Start the simulation



