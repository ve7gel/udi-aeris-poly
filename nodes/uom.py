#
#  Unit of Measure configuration function
#
#  Return a dictionary with driver names as the key and the UOM for
#  the requested unit configuration.
#
#  valid unit configurations are:
#   metric, imperial, si (same as metric), us (same as imperial), uk
#
#  Ideally, there should be no conflicts between forecast and current
#  condition driver types

class uom:
    class ConstError(TypeError): pass

    def __init__(self, units):
        self.__dict__['ST'] = 2   # node server status
        self.__dict__['CLITEMP'] = 4   # temperature
        self.__dict__['CLIHUM'] = 22   # humidity
        self.__dict__['BARPRES'] = 117 # pressure
        self.__dict__['WINDDIR'] = 76  # direction
        self.__dict__['DEWPT'] = 4     # dew point
        self.__dict__['SOLRAD'] = 74   # solar radiation
        self.__dict__['RAINRT'] = 46   # rain rate
        self.__dict__['GV0'] = 4       # max temp
        self.__dict__['GV1'] = 4       # min temp
        self.__dict__['GV2'] = 4       # ??feels like
        self.__dict__['GV3'] = 4       # heat index  
        self.__dict__['GV4'] = 4       # wind chill
        self.__dict__['SPEED'] = 32    # wind speed
        self.__dict__['GV5'] = 32      # wind gusts
        self.__dict__['GV6'] = 82      # rain
        self.__dict__['GV7'] = 32      # wind max
        self.__dict__['GV8'] = 32      # wind min  
        self.__dict__['GV9'] = 56      # moon phase
        self.__dict__['GV10'] = 56     # ozone
        self.__dict__['GV11'] = 25     # climate coverage
        self.__dict__['GV12'] = 25     # climate intensity
        self.__dict__['GV13'] = 25     # climate conditions
        self.__dict__['GV14'] = 22     # cloud conditions
        self.__dict__['GV15'] = 82     # snow depth
        self.__dict__['DISTANC'] = 83  # visibility (kilometers)
        self.__dict__['UV'] = 71       # UV index
        self.__dict__['GV17'] = 56     # Air Quality
        self.__dict__['GV18'] = 22     # chance of precipitation
        self.__dict__['GV19'] = 25     # day of week
        self.__dict__['GV20'] = 106    # ETo
        self.__dict__['PRECIP'] = 83   # precipitation

        if units == 'uk':
            self.__dict__['SPEED'] = 48    # wind speed
            self.__dict__['GV5'] = 48      # wind gusts
            self.__dict__['GV6'] = 105     # rain
            self.__dict__['GV7'] = 48      # max wind
            self.__dict__['GV8'] = 48      # min wind  
            self.__dict__['GV15'] = 105    # snow depth
            self.__dict__['DISTANC'] = 116 # visibility
            self.__dict__['PRECIP'] = 83   # precipitation
            self.__dict__['GV20'] = 120    # ETo

        if units == 'imperial' or units == 'us':
            self.__dict__['CLITEMP'] = 17  # temperature
            self.__dict__['BARPRES'] = 23  # pressure
            self.__dict__['DEWPT'] = 17    # dew point
            self.__dict__['GV0'] = 17      # max temp
            self.__dict__['GV1'] = 17      # min temp
            self.__dict__['GV2'] = 17      # feels like
            self.__dict__['GV3'] = 17      # ??feels like
            self.__dict__['GV4'] = 17      # wind chill
            self.__dict__['SPEED'] = 48    # wind speed
            self.__dict__['GV5'] = 48      # wind gusts
            self.__dict__['GV6'] = 105     # rain
            self.__dict__['GV7'] = 48      # max wind
            self.__dict__['GV8'] = 48      # min wind   
            self.__dict__['GV15'] = 105    # snow depth
            self.__dict__['DISTANC'] = 116 # visibility
            self.__dict__['PRECIP'] = 105  # precipitation
            self.__dict__['GV20'] = 120    # ETo

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const({})".format(name))

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError("Can't unbind const({})".format(name))
        raise NameError(name)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

    def __getitem__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]


"""
def get_uom(units):
    unit_cfg = units.lower()

    if unit_cfg == 'metric' or unit_cfg == 'si' or unit_cfg.startswith('m'):
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 4,   # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 117, # pressure
            'WINDDIR': 76,  # direction
            'DEWPT': 4,     # dew point
            'SOLRAD': 74,   # solar radiation
            'RAINRT': 46,   # rain rate
            'GV0': 4,       # max temp
            'GV1': 4,       # min temp
            'GV2': 4,       # ??feels like
            'GV3': 4,       # heat index  
            'GV4': 4,       # wind chill
            'SPEED': 32,    # wind speed
            'GV5': 32,      # wind gusts
            'GV6': 82,      # rain
            'GV7': 32,      # wind max
            'GV8': 32,      # wind min  
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 82,     # snow depth
            'DISTANC': 83,  # visibility (kilometers)
            'UV': 71,       # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 106,    # ETo
        }
    elif unit_cfg == 'uk':
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 4,   # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 117, # pressure
            'WINDDIR': 76,  # direction
            'DEWPT': 4,     # dew point
            'SOLRAD': 74,   # solar radiation
            'RAINRT': 24,   # rain rate
            'GV0': 4,       # max temp
            'GV1': 4,       # min temp
            'GV2': 4,       # feels like
            'GV3': 4,       # ??feels like
            'GV4': 4,       # wind chill
            'SPEED': 48,    # wind speed
            'GV5': 48,      # wind gusts
            'GV6': 105,     # rain
            'GV7': 48,      # max wind
            'GV8': 48,      # min wind  
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 105,    # snow depth
            'DISTANC': 116, # visibility
            'UV': 71,       # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 120,    # ETo
        }
    else:
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 17,  # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 23,  # pressure
            'WINDDIR': 76,  # direction
            'DEWPT': 17,    # dew point
            'SOLRAD': 74,   # solar radiation
            'RAINRT': 24,   # rain rate
            'GV0': 17,      # max temp
            'GV1': 17,      # min temp
            'GV2': 17,      # feels like
            'GV3': 17,      # ??feels like
            'GV4': 17,      # wind chill
            'SPEED': 48,    # wind speed
            'GV5': 48,      # wind gusts
            'GV6': 105,     # rain
            'GV7': 48,      # max wind
            'GV8': 48,      # min wind   
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 105,    # snow depth
            'DISTANC': 116, # visibility
            'UV': 71,       # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 120,    # ETo
        }

    return uom
"""
