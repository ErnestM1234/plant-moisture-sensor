import time



class StateMachine:


  def __init__(self):
    self.states = {}
    self.initial_state = None
    self.current_state = None
    self.next_state = None



  def get_state(self):
    return self.current_state



  def add_initial_state(self, name, callback=None):

    self.add_state(name, callback)
    self.initial_state = name


  def add_state(self, name, callback=None):

    # add state to dictionary
    self.states[name] = callback

  def getState(self):
    return self.current_state

  def execute_state(self):

    # get the current state
    if self.current_state or self.current_state not in self.states:
      return
    
    # execute
    self.current_state = self.states[self.current_state]()


  def execute(self, delay=0):

    # check initial state
    if self.initial_state == None:
      raise Exception('Initial state not set')

    # execute states
    while True:
      print('State:', self.current_state)
      self.execute_state()
      if self.current_state == None:
        break
      time.sleep(delay)

    
  def reset(self):
    print('Resetting to initial state')
    self.current_state = self.initial_state

