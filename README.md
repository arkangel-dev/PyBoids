# PyBoids
A horribly written library to simulate boids in python.  This thing still needs some fixing.

## How this shit works

```python
import PyBoids

env = PyBoids.Environment((500, 500)) # create environment
env.AddObservingMember() # Add an observing bord
env.StartConsole() # Start the console
env.Start() # Start the simulation
```

