from probestrategy import ProbeStrategy

class TestProbeStrategy(ProbeStrategy):
    def __init__(self):
        self.initial_probe_level = None
   
    def get_current_estimate(self):
        pass
        
    def get_next_probe_level(self):
        pass
        
    def get_next_probe_level_as_string(self):
        pass
        
    def get_next_stimulus_id(self):
        pass
        
    def is_finished(self):
        pass
        
    def store_trial_result(self):
        pass
        
    def setup_string_cli(self):
        self.initial_probe_level = self.prompt_for_user_input(
            prompt='Enter a string', ui='cli', input_type=str)
            
    def setup_string_gui(self):
        self.initial_probe_level = self.prompt_for_user_input(
            prompt='Enter a string', ui='gui', input_type=str)       

    def setup_float_cli(self):
        self.initial_probe_level = self.prompt_for_user_input(
            prompt='Enter a float', ui='cli', input_type=float)
            
    def setup_float_gui(self):
        self.initial_probe_level = self.prompt_for_user_input(
            prompt='Enter a float', ui='gui', input_type=float)  
        
# if True:
#     config = {'initial_probe_level': None,
#               'max_num_trials': 3}
#     ps = MultipleFixedProbeLevels(config)
#     print(f'initial_probe_level: {ps.initial_level}')
#
# if True:
#     config = {'initial_probe_level': 12,
#               'max_num_trials': 3}
#     ps = MultipleFixedProbeLevels(config)
#     print(f'initial_probe_level: {ps.initial_level}')

if True:
    ps = TestProbeStrategy()
    print(f'initial_probe_level: {ps.initial_probe_level}')
    ps.setup_string_cli()
    print(f'initial_probe_level: {ps.initial_probe_level}')
    ps.setup_string_gui()
    print(f'initial_probe_level: {ps.initial_probe_level}')
    ps.setup_float_cli()
    print(f'initial_probe_level: {ps.initial_probe_level}')
    ps.setup_float_gui()
    print(f'initial_probe_level: {ps.initial_probe_level}')
    
# if True:
#     config = {'initial_probe_level': 12,
#               'max_num_trials': 3}
#     ps = MultipleFixedProbeLevels(config)
#     print(f'initial_probe_level: {ps.initial_level}')