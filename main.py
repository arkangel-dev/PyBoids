import bird

env = bird.Environment()
env.AddBoidArray(30)
env.AddObservingMember()
env.Start()