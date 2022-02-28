# Declare your custom signal-check action like so
#     "action": {
#       "file": "example_action.py",
#       "parameters": {
#           "parameter-1": "example-parameter!"
#       }
#     }

# The function signature MUST BE EXACTLY LIKE THIS
def custom_action(parameters, condition, data):
    print('Signal check caught an error! This is the parameter passed: ' + parameters['parameter-1'])
