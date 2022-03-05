# Declare your custom signal-check action like so
#     "cue": {
#       "file": "example_cue.py",
#       "parameters": {
#           "parameter-1": "example-parameter!"
#       }
#     }

# The function signature MUST BE EXACTLY LIKE THIS
def custom_cue(parameters):
    print('Cue fired!\nParameter: ' + parameters['parameter-1'])