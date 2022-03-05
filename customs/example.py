# Declare your custom pre-processing step like so
#     {
#       "type": "CUSTOM",
#       "parameters": {
#         "file": "example.py",
#         "parameter-1": 100,
#         "parameter-2": 1
#       }
#     }

# The function signature MUST BE EXACTLY LIKE THIS
def custom_process(parameters, data):
    # Declare imports here (make sure needed packages are already installed)
    from brainflow import DataFilter
    # Modify the input data
    for channel in data:
        DataFilter.perform_rolling_filter(channel, parameters['parameter-1'], parameters['parameter-2'])
