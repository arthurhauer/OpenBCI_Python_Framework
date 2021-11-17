OpenBCI - Python interface framework

# CYTON_BOARD physical coniguration
    
CYTON switch must have 'PC' selected

Dongle switch must have 'GPIO_6' selected

# Pre-Processing Node configuration examples:

Allowed preprocessing node "type" values: 
> "CUSTOM" | "DETREND" | "FILTER" | "DOWNSAMPLE"

## Filters

Allowed filter node "filter" parameter values:
> "BESSEL" | "BUTTERWORTH" | "CHEBYSHEV_TYPE_1"

### Band
#### Band Pass

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
#### Band Stop

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
### Cut-Off
#### Low Pass

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
#### High Pass

In the following example, we configure a 80Hz high pass 3rd order Butterworth filter
```
{
    "type":"FILTER",               // Preprocessing node type
    "parameters":{                 // Node parameters
        "type": "LOWPASS",         // Filter action
        "filter": "BUTTERWORTH",   // Filter type
        "order": 3,                // Filter order
        "cutoff-freq": 80,         // Cut-off frequency
    }
}
```

## Detrend
Allowed detrend node "type" parameter values:
> "NONE" | "CONSTANT" | "LINEAR"

In the following example, we configure a linear detrend
```
{
    "type":"DETREND",       // Preprocessing node type
    "parameters":{          // Node parameters
        "type": "LINEAR"    // Detrend type
    }
}
```

## Downsample
Allowed detrend node "type" parameter values:
> "MEAN" | "MEDIAN" | "EACH"

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
## Custom

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
