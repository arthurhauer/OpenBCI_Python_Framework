OpenBCI - Python interface framework

# CYTON_BOARD physical coniguration
    
CYTON switch must have 'PC' selected

Dongle switch must have 'GPIO_6' selected

# Pre-Processing Node configuration examples:

Allowed preprocessing node "type" values: "CUSTOM" | "DETREND" | "FILTER" | "DOWNSAMPLE"

## Filters

Allowed "filter" parameter values: "BESSEL" | "BUTTERWORTH" | "CHEBYSHEV_TYPE_1"

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
