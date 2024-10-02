import winsound

def custom_cue(parameters):
    print(parameters['message'])
    winsound.Beep(1000, 100)