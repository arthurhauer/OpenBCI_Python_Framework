import winsound


def custom_cue(parameters):
    print(parameters['message'])
    winsound.Beep(parameters['frequency'], parameters['duration'])