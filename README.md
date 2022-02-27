OpenBCI - Python interface framework

# CYTON_BOARD physical coniguration
    
CYTON switch must have 'PC' selected

Dongle switch must have 'GPIO_6' selected

# Using with Windows

To use with Windows, simply specify wich COM port your board is using.

# Using with Linux

To use with Linux, run python as sudo, and specify the path to the serial port your board is using.

# Configuration JSON

## General

Here, we configure our framework to work with as many parallel threads as the host can handle, while also setting our GUI graph window size to 4.

```
"general":{
    "maximum-parallel-jobs":-1,     \\ Maximum parallel jobs. Set to -1 to infinite, 1 for 1 and so on
    "graph": {                      \\ Graphing options
      "window-size": 4              \\ Graphing window size
    }
}
```

## Open-BCI
Allowed "board" parameter values:

>"PLAYBACK_FILE_BOARD"
 
>"STREAMING_BOARD"

>"SYNTHETIC_BOARD"

>"CYTON_BOARD"

>"GANGLION_BOARD"

>"CYTON_DAISY_BOARD"

>"GALEA_BOARD"

>"GANGLION_WIFI_BOARD"

>"CYTON_WIFI_BOARD"

>"CYTON_DAISY_WIFI_BOARD"

>"BRAINBIT_BOARD"

>"UNICORN_BOARD"

>"CALLIBRI_EEG_BOARD"

>"CALLIBRI_EMG_BOARD"

>"CALLIBRI_ECG_BOARD"

>"NOTION_1_BOARD"

>"NOTION_2_BOARD"

>"IRONBCI_BOARD"

>"GFORCE_PRO_BOARD"

>"FREEEEG32_BOARD"

>"BRAINBIT_BLED_BOARD"

>"GFORCE_DUAL_BOARD"

>"GALEA_SERIAL_BOARD"

>"MUSE_S_BLED_BOARD"

>"MUSE_2_BLED_BOARD"

>"CROWN_BOARD"

>"ANT_NEURO_EE_410_BOARD"

>"ANT_NEURO_EE_411_BOARD"

>"ANT_NEURO_EE_430_BOARD"

>"ANT_NEURO_EE_211_BOARD"

>"ANT_NEURO_EE_212_BOARD"

>"ANT_NEURO_EE_213_BOARD"

>"ANT_NEURO_EE_214_BOARD"

>"ANT_NEURO_EE_215_BOARD"

>"ANT_NEURO_EE_221_BOARD"

>"ANT_NEURO_EE_222_BOARD"

>"ANT_NEURO_EE_223_BOARD"

>"ANT_NEURO_EE_224_BOARD"

>"ANT_NEURO_EE_225_BOARD"

>"ENOPHONE_BOARD"

>"MUSE_2_BOARD"

>"MUSE_S_BOARD"

Here we can configure the board we'll be working with

```
"open_bci": {
    "log_level": "TRACE",               \\ Board log level
    "board": "SYNTHETIC_BOARD",         \\ Board type
    "data-callback-frequency-ms": 50,   \\ How much time to wait before getting new buffered data from the board
    "communication": {                  \\ Communication configurations
      "serial_port": "/dev/ttyUSB0"     \\ Serial port
    }
}
```

## Pre-Processing

Pre-processing steps are configured as a JSON list, as such:

```
"preprocessing":[]
```

Then, each step is executed in the same order it was declared in respect to other steps. For instance, if one declares something like the following, the framework will first detrend the data, and then apply a lowpass filter.

```
"preprocessing":[
    {
    "type":"DETREND",       // Preprocessing node type
    "parameters":{          // Node parameters
        "type": "LINEAR"    // Detrend type
        }
    },
    {
    "type":"FILTER",               // Preprocessing node type
    "parameters":{                 // Node parameters
        "type": "LOWPASS",         // Filter action
        "filter": "BUTTERWORTH",   // Filter type
        "order": 1,                // Filter order
        "cutoff-freq": 50,         // Cut-off frequency
        }
    }
]
```


Allowed preprocessing node "type" values: 
> "CUSTOM"

> "DETREND"

> "FILTER"

> "DOWNSAMPLE"

> "SIGNAL_CHECK"

### Filters

Allowed filter node "filter" parameter values:
> "BESSEL"

> "BUTTERWORTH"

> "CHEBYSHEV_TYPE_1"

When using > "CHEBYSHEV_TYPE_1", one must provide a ripple value, declared as a float in the parameters field (see Band Stop example).

#### Band
##### Band Pass

In the following example, we configure a 50Hz-150Hz band pass 2nd order Bessel filter
```
{
    "type":"FILTER",            // Preprocessing node type
    "parameters":{              // Node parameters
        "type": "BANDPASS",     // Filter action
        "filter": "BESSEL",     // Filter type
        "order": 2,             // Filter order
        "center-freq": 100,     // Band center frequency
        "band-width": 50        // Band width
    }
}
```
##### Band Stop

In the following example, we configure a 30Hz-70Hz band pass 2nd order type 1 Chebyshev filter, with 0.2 ripple
```
{
    "type":"FILTER",                    // Preprocessing node type
    "parameters":{                      // Node parameters
        "type": "BANDSTOP",             // Filter action
        "filter": "CHEBYSHEV_TYPE_1",   // Filter type
        "order": 2,                     // Filter order
        "ripple": 0.2,                  // Chebyshev ripple
        "center-freq": 50,              // Band center frequency
        "band-width": 20                // Band width
    }
}
```
#### Cut-Off
##### Low Pass

In the following example, we configure a 50Hz low pass 1st order Butterworth filter
```
{
    "type":"FILTER",               // Preprocessing node type
    "parameters":{                 // Node parameters
        "type": "LOWPASS",         // Filter action
        "filter": "BUTTERWORTH",   // Filter type
        "order": 1,                // Filter order
        "cutoff-freq": 50,         // Cut-off frequency
    }
}
```
##### High Pass

In the following example, we configure a 80Hz high pass 3rd order Butterworth filter
```
{
    "type":"FILTER",               // Preprocessing node type
    "parameters":{                 // Node parameters
        "type": "HIGHPASS",        // Filter action
        "filter": "BUTTERWORTH",   // Filter type
        "order": 3,                // Filter order
        "cutoff-freq": 80,         // Cut-off frequency
    }
}
```

### Detrend
Allowed detrend node "type" parameter values:
> "NONE"

> "CONSTANT"

> INEAR"

In the following example, we configure a linear detrend
```
{
    "type":"DETREND",       // Preprocessing node type
    "parameters":{          // Node parameters
        "type": "LINEAR"    // Detrend type
    }
}
```

### Downsample
Allowed detrend node "type" parameter values:
> "MEAN"

>"MEDIAN"

>"EACH"

In the following example, we configure a median based downsampler
```
{
    "type":"DOWNSAMPLE",    // Preprocessing node type
    "parameters":{          // Node parameters
        "type": "MEDIAN"    // Detrend type,
        "period": 100       // Downsampling period, in samples
    }
}
```
### Custom

In the following example, we configure a custom preprocessing node, based on user provided script.
In this case, the custom script performs a rolling filtering of the input data.

```
{
    "type":"CUSTOM",            // Preprocessing node type
    "parameters":{              // Node parameters
        "file": "example.py",   // File containing custom script, located in 'projectRoot/customs/',
        "parameter-1": 100,     // First parameter passed to custom script
        "parameter-2": 1,       // Second parameter passed to custom script
    }
}
```
In order to work properly, one must declare the custom script function like so:

```
def custom_process(parameters, data):
    # All needed imports should be declared here (make sure needed packages are already installed)
    from brainflow import DataFilter
    # Modify the input data
    DataFilter.perform_rolling_filter(data, parameters['parameter-1'], parameters['parameter-2'])
```
Also, each custom script file must contain exactly one function definition, and it's signature should be declared exactly as shown in the example above.

Notice that the input data is modified in-place.

### Signal Check

Signal check preprocessing node allows us to verify if an EEG electrode is well connected.
This is done by verifying the given electrode's signal RMS and amplitude, as well as the singal's root frequency, to check wether it's the same as the power grid's.
On confirming that the signal is no good, the framework will execute a given user-defined action, which could be turning on an LED, showing a message on screen, etc.
The definition of the user-defined action is made in a similar fashion as the custom preprocessing node, mentioned previously.
In the following example, we configure a signal check preprocessing node, where the minimum signal amplitude should be 200 m.u., minimum signal RMS should be 5 uA, and the local powergrid frequency is 60hHz.

```
    {
       "type": "SIGNAL_CHECK",                      // Preprocessing node type
       "parameters": {                              // Node parameters
         "action": {                                // User-defined action
           "file": "example_action.py",             // Action containing file, located in 'projectRoot/signal_check/action'
           "parameters": {                          // Action parameters
             "parameter-1": "example-parameter!"    // First parameter passed to user-defined action
           }
         },
         "power-grid-frequency": 60,                // Powergrid frequency
         "min-amplitude": 200,                      // Minimum signal amplitude. Anything below this is considered bad.
         "min-rms": 5                               // Minimum signal RMS. Anything below this is considered bad.
       }
     }
```

The user-defined action should be contained in a python script file, located in 'projectRoot/signal_check/action', and defined as such:

```
def action(parameters, data):
    print('Signal check caught a bad signal! This is the parameter passed: ' + parameters['parameter-1'])
```

Also, each action script file must contain exactly one function definition, and it's signature should be declared exactly as shown in the example above.
