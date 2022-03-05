import enum


class PreProcessingType(enum.IntEnum):
    CUSTOM = 0
    DETREND = 1
    FILTER = 2
    DOWNSAMPLE = 3
    DENOISE = 4
    TRANSFORM = 5
    SMOOTH = 6
    SIGNAL_CHECK = 7
    FEATURE_EXTRACT = 8
