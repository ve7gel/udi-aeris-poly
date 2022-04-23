"""
Do I want this encapsulated in a class or not?

export:
    query_conditions(update_function, force)
    query_forecasts(force)

"""
import udi_interface
import requests
import time
import datetime
from nodes import weather_codes as wx

LOGGER = udi_interface.LOGGER

"""
The WeatherData class holds the mapping of drivers to UOM, query tags,
and possibly parsing functions.

Internally this looks like:
    { driver : {uom: x, tag: '', ftag: '', parse: (function)}}
"""
class WeatherData:
    class ConstError(TypeError): pass

    def __init__(self, units):
        self.__dict__['isMetric'] = True
        self.__dict__['ST']      = {'uom': 2,   'tag': '',                'ftag': '', 'parse': None}   # node server status
        self.__dict__['CLITEMP'] = {'uom': 4,   'tag': 'tempC',           'ftag': 'tempC', 'parse': None}   # temperature
        self.__dict__['CLIHUM']  = {'uom': 22,  'tag': 'humidity',        'ftag': 'humidity', 'parse': None}   # humidity
        self.__dict__['BARPRES'] = {'uom': 117, 'tag': 'pressureMB',      'ftag': 'pressureMB', 'parse': None} # pressure
        self.__dict__['WINDDIR'] = {'uom': 76,  'tag': 'windDirDEG',      'ftag': 'windDirDEG', 'parse': None}  # direction
        self.__dict__['DEWPT']   = {'uom': 4,   'tag': 'dewpointC',       'ftag': 'dewpointC', 'parse': None}     # dew point
        self.__dict__['SOLRAD']  = {'uom': 74,  'tag': 'solradWM2',       'ftag': 'solradWM2', 'parse': None}   # solar radiation
        self.__dict__['RAINRT']  = {'uom': 46,  'tag': '',                'ftag': '', 'parse': None}   # rain rate
        self.__dict__['SPEED']   = {'uom': 32,  'tag': 'windSpeedKPH',    'ftag': 'windSpeedKPH', 'parse': None}    # wind speed
        self.__dict__['DISTANC'] = {'uom': 83,  'tag': 'visibilityKM',    'ftag': 'visibilityKM', 'parse': None}  # visibility
        self.__dict__['UV']      = {'uom': 71,  'tag': 'uvi',             'ftag': 'uvi', 'parse': None}       # UV index
        self.__dict__['AQI']     = {'uom': 56,  'tag': '',                'ftag': '', 'parse': None}     # Air Quality
        self.__dict__['ETO']     = {'uom': 106, 'tag': '',                'ftag': '', 'parse': None}    # ETo
        self.__dict__['GUST']    = {'uom': 32,  'tag': 'windGustKPH',     'ftag': 'windGustKPH', 'parse': None}      # wind gusts
        self.__dict__['HEATIX']  = {'uom': 4,   'tag': 'heatindexC',      'ftag': 'heatindexC', 'parse': None}       # heat index
        self.__dict__['MOON']    = {'uom': 56,  'tag': '',                'ftag': '', 'parse': None}      # moon phase
        self.__dict__['OZONE']   = {'uom': 56,  'tag': '',                'ftag': '', 'parse': None}     # ozone
        self.__dict__['POP']     = {'uom': 22,  'tag': 'pop',             'ftag': 'pop', 'parse': None}     # chance of precipitation
        self.__dict__['PRECIP']  = {'uom': 82,  'tag': 'totalMM',         'ftag': 'precipMM', 'parse': None}      # rain
        self.__dict__['WINDCH']  = {'uom': 4,   'tag': 'windchillC',      'ftag': 'windchillC', 'parse': None}       # wind chill
        self.__dict__['LUMIN']   = {'uom': 36,  'tag': '',                'ftag': '', 'parse': None}       # luminance
        self.__dict__['GV0']     = {'uom': 4,   'tag': 'maxTempC',        'ftag': 'maxTempC', 'parse': None}       # max temp
        self.__dict__['GV1']     = {'uom': 4,   'tag': 'minTempC',        'ftag': 'minTempC', 'parse': None}       # min temp
        self.__dict__['GV2']     = {'uom': 4,   'tag': 'feelslikeC',      'ftag': 'feelslikeC', 'parse': None}       # ??feels like
        self.__dict__['GV7']     = {'uom': 32,  'tag': 'windSpeedMaxKPH', 'ftag':'windSpeedMaxKPH', 'parse': None}      # wind max
        self.__dict__['GV8']     = {'uom': 32,  'tag': 'windSpeedMinKPH', 'ftag':'windSpeedMinKPH', 'parse': None}      # wind min  
        self.__dict__['GV11']    = {'uom': 25,  'tag': 'weatherCoded',    'ftag': 'weatherPrimaryCoded', 'parse': None} # climate coverage
        self.__dict__['GV12']    = {'uom': 25,  'tag': 'weatherCoded',    'ftag': 'weatherPrimaryCoded', 'parse': None} # climate intensity
        self.__dict__['GV13']    = {'uom': 25,  'tag': 'weatherCoded',    'ftag': 'weatherPrimaryCoded', 'parse': None} # climate conditions
        self.__dict__['GV14']    = {'uom': 22,  'tag': 'sky',             'ftag': 'sky', 'parse': None}     # cloud conditions
        self.__dict__['GV15']    = {'uom': 82,  'tag': 'snowDepthCM',     'ftag': 'snowCM', 'parse': None}     # snow depth
        self.__dict__['GV19']    = {'uom': 25,  'tag': '',                'ftag': '', 'parse': None}     # day of week

        if units == 'uk':
            self.__dict__['isMetric'] = False
            self.__dict__['SPEED']   = {'uom': 48,  'tag': 'windSpeedMPH',    'ftag': 'windSpeedMPH', 'parse': None}    # wind speed
            self.__dict__['DISTANC'] = {'uom': 116, 'tag': 'visibilityMI',    'ftag': 'visibilityMI', 'parse': None} # visibility
            self.__dict__['ETO']     = {'uom': 120, 'tag': '',                'ftag': '', 'parse': None}    # ETo
            self.__dict__['GUST']    = {'uom': 48,  'tag': 'windGustMPH',     'ftag':'windGustMPH', 'parse': None}      # wind gusts
            self.__dict__['PRECIP']  = {'uom': 105, 'tag': 'totalIN',         'ftag': 'precipIN', 'parse': None}     # rain
            self.__dict__['GV7']     = {'uom': 48,  'tag': 'windSpeedMaxMPH', 'ftag': 'windSpeedMaxMPH', 'parse': None}      # max wind
            self.__dict__['GV8']     = {'uom': 48,  'tag': 'windSpeedMinMPH', 'ftag': 'windSpeedMinMPH', 'parse': None}      # min wind  
            self.__dict__['GV15']    = {'uom': 105, 'tag': 'snowDepthIN',     'ftag': 'snowIN', 'parse': None}    # snow depth

        if units == 'imperial' or units == 'us':
            self.__dict__['isMetric'] = False
            self.__dict__['CLITEMP'] = {'uom': 17,  'tag': 'tempF',           'ftag': 'tempF',           'parse': None} # temperature
            self.__dict__['BARPRES'] = {'uom': 23,  'tag': 'pressureIN',      'ftag': 'pressureIN',      'parse': None} # pressure
            self.__dict__['DEWPT']   = {'uom': 17,  'tag': 'dewpointF',       'ftag': 'dewpointF',       'parse': None} # dew point
            self.__dict__['SPEED']   = {'uom': 48,  'tag': 'windSpeedMPH',    'ftag': 'windSpeedMPH',    'parse': None} # wind speed
            self.__dict__['DISTANC'] = {'uom': 116, 'tag': 'visibilityMI',    'ftag': 'visibilityMI',    'parse': None} # visibility
            self.__dict__['ETO']     = {'uom': 120, 'tag': '',                'ftag': '',                'parse': None} # ETo
            self.__dict__['GUST']    = {'uom': 48,  'tag': 'windGustMPH',     'ftag': 'windGustMPH',     'parse': None} # wind gusts
            self.__dict__['HEATIX']  = {'uom': 17,  'tag': 'heatindexF',      'ftag': 'heatindexF',      'parse': None} # ??feels like
            self.__dict__['PRECIP']  = {'uom': 105, 'tag': 'totalIN',         'ftag': 'precipIN',        'parse': None} # rain
            self.__dict__['WINDCH']  = {'uom': 17,  'tag': 'windchillF',      'ftag': 'windchillF',      'parse': None} # wind chill
            self.__dict__['GV0']     = {'uom': 17,  'tag': 'maxTempF',        'ftag': 'maxTempF',        'parse': None} # max temp
            self.__dict__['GV1']     = {'uom': 17,  'tag': 'minTempF',        'ftag': 'minTempF',        'parse': None} # min temp
            self.__dict__['GV2']     = {'uom': 17,  'tag': 'feelslikeF',      'ftag': 'feelslikeF',      'parse': None} # feels like
            self.__dict__['GV7']     = {'uom': 48,  'tag': 'windSpeedMaxMPH', 'ftag': 'windSpeedMaxMPH', 'parse': None} # max wind
            self.__dict__['GV8']     = {'uom': 48,  'tag': 'windSpeedMinMPH', 'ftag': 'windSpeedMinMPH', 'parse': None} # min wind   
            self.__dict__['GV15']    = {'uom': 105, 'tag': 'snowDepthIN',     'ftag': 'snowIN',          'parse': None} # snow depth

        self.__dict__['GV11']['parse'] = 'self._parse_coverage_codes'
        self.__dict__['GV12']['parse'] = 'self._parse_intensity_codes'
        self.__dict__['GV13']['parse'] = 'self._parse_weather_codes'

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

    def uom(self, name):
        return self.__dict__[name]['uom']

    def _parse_weather_codes(self, code):
        # looks like ::H,::SC
        # first split on ','

        code = code.split(',')[0]
        code = code.split(':')[2]
        code_map = {
            'A': 0,   # hail
            'BD': 1,  # blowing dust
            'BN': 2,  # blowing sand
            'BR': 3,  # mist
            'BS': 4,  # blowing snow
            'BY': 5,  # blowing spray
            'F': 6,   # fog
            'FR': 7,  # frost
            'H': 8,   # haze
            'IC': 9,  # ice crystals
            'IF': 10, # ice fog
            'IP': 11, # ice pellets / Sleet
            'K': 12,  # smoke
            'L': 13,  # drizzle
            'R': 14,  # rain
            'RW': 15, # rain showers
            'RS': 16, # rain/snow mix
            'SI': 17, # snow/sleet mix
            'WM': 18, # wintry mix (sno, sleet, rain)
            'S': 19,  # snow
            'SW': 20, # snow showers
            'T': 21,  # Thunderstorms
            'UP': 22, # unknown precipitation
            'VA': 23, # volcanic ash
            'WP': 24, # waterspouts
            'ZF': 25, # freezing fog
            'ZL': 26, # freezing drizzle
            'ZR': 27, # freezing rain
            'ZY': 28, # freezing spray
            'CL': 29, # Clear
            'FW': 30, # Fair/Mostly sunny
            'SC': 31, # Partly cloudy
            'BK': 32, # Mostly cloudy
            'OV': 33, # Cloudy/Overcast
            }

        if code in code_map:
            return code_map[code]

        return 22

    def _parse_intensity_codes(self, code):
        code = code.split(',')[0]
        code = code.split(':')[1]
        code_map = {
            'VL': 1,  # very light
            'L': 2,   # light
            'H': 3,   # heavy
            'VH': 4,  # very heavy
            }
        if code in code_map:
            return code_map[code]
        return 0  # moderate

    def _parse_coverage_codes(self, code):
        code = code.split(',')[0]
        code = code.split(':')[0]
        code_map = {
            'AR': 0,  # areas of
            'BR': 1,  # brief
            'C':  2,  # chance of
            'D':  3,  # definite
            'FQ': 4,  # frequent
            'IN': 5,  # intermittent
            'IS': 6,  # isolated
            'L':  7,  # likely
            'NM': 8,  # numerous
            'O':  9,  # occasional
            'PA': 10,  # patchy
            'PD': 11,  # periods of
            'S':  12,  # slight chance
            'SC': 13,  # scattered
            'VC': 14,  # in the vicinity/nearby
            'WD': 15,  # widespread
            }
        if code in code_map:
            return code_map[code]
        return 16

    def parse(self, name, data):
        tag = self.__dict__[name]['tag']
        if tag in data:
            if self.__dict__[name]['parse'] is not None:
                return eval(self.__dict__[name]['parse'])(data[tag])
            else:
                return data[tag]
        raise self.ConstError("{}: {} not found in data.".format(name, tag))

    def fparse(self, name, data):
        tag = self.__dict__[name]['ftag']
        if tag in data:
            if self.__dict__[name]['parse'] is not None:
                return eval(self.__dict__[name]['parse'])(data[tag])
            else:
                return data[tag]
        raise self.ConstError("{}: {} not found in data.".format(name, tag))




class queries(object):
    def __init__(self, polyglot):
        self.poly = polyglot

        # initialize properties
        self.__dict__['units'] = 'metric'
        self.__dict__['days'] = 0
        self.__dict__['location'] = ''
        self.__dict__['client_id'] = ''
        self.__dict__['client_secret'] = ''
        self.__dict__['plant_type'] = 0
        self.__dict__['elevation'] = 0
        self.__dict__['configured'] = False
        self.api = 'http://api.aerisapi.com/'
        self.latitude = 0
        self.tag = {}



    def __setattr__(self, key, value):
        self.__dict__[key] = value

    # Make and call the actual query URL
    def _get_weather_data(self, extra, lat=None, long=None):
        request = self.api + extra + '/'

        request += self.location
        request += '?client_id=' + self.client_id
        request += '&client_secret=' + self.client_secret

        if extra == 'forecasts':
            request += '&filter=mdnt2mdnt'
            request += '&precise'
            request += '&limit=' + str(self.days)

        if extra == 'observations/summary':
            request += '&fields=periods.summary.precip'

        #FIXME: add unit support if available
        #request += '&units=' + self.units

        LOGGER.debug('request = %s' % request)

        try:
            c = requests.get(request)
            jdata = c.json()
            c.close()
            LOGGER.debug(jdata)
        except:
            LOGGER.error('HTTP request failed for api.aerisapi.com')
            jdata = None

        return jdata

    def query_conditions(self, address, units, force):
        # Query for the current conditions. We can do this fairly
        # frequently, probably as often as once a minute.

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        precipitation = 0
        wmap = WeatherData(units)
        n = self.poly.getNode(address)
        prec = 1  ## TODO: this may need to go in wmap too or can we pull this from editor?

        try:
            jdata = self._get_weather_data('observations')
            if jdata == None:
                LOGGER.error('Current condition query returned no data')
                return
            '''
            Data from query has multiple units. Which one we want to use depends
            on what the user has selected.  Since we set the node to metric by
            default, lets just use those for testing.
            '''
        
            #jdata['response']['ob']['tempC']
            if 'response' not in jdata:
                LOGGER.error('No response object in query response.')
                return

            if 'ob' not in jdata['response']:
                LOGGER.error('No observation object in query response.')
                return

            if 'loc' in jdata['response']:
                if 'lat' in jdata['response']['loc']:
                    self.latitude = float(jdata['response']['loc']['lat'])
                else:
                    LOGGER.error('No latitude data in response.')
            else:
                LOGGER.error('No location data in response.')

            ob = jdata['response']['ob']

            for drv in n.drivers:
                if drv['driver'] == 'PRECIP':
                    continue # this comes from a different query
                if drv['driver'] == 'ST':
                    continue # Skip this

                try:
                    v = wmap.parse(drv['driver'], ob)
                    if v == None or v == "None":
                        v = "0"
                    if drv['driver'] == 'GV15' and wmap.isMetric:
                        v = v * 10 # snow depth is in cm, convert to mm
                    n.setDriver(drv['driver'], round(float(v), prec), True, force, wmap.uom(drv['driver']))
                    LOGGER.debug('setDriver (%s, %f)' %(drv['driver'], float(v)))
                except Exception as e:
                    LOGGER.warning('Error updating {}: {}'.format(drv['driver'], e))

        except Exception as e:
            LOGGER.error('Current observation update failure: {}'.format(e))

        """ 
        We get precipitation from a different query. 
        """
        try:
            # Get precipitation summary
            jdata = self._get_weather_data('observations/summary')
            if jdata == None:
                LOGGER.error('Precipitation summary query returned no data')
                return
            if 'response' not in jdata:
                LOGGER.error('No response object in query response.')
                return
            #LOGGER.debug(jdata)
            if type(jdata['response']) is list:
                rd = jdata['response'][0]['periods'][0]['summary']
            else:
                rd = jdata['response']['periods'][0]['summary']

            if 'precip' in rd:
                if 'precip_summary' in rd['precip']:
                    LOGGER.debug('Setting precipitation to: ' + str(rd['precip'][self.tag['precip_summary']]))
                    v = wmap.parse('PRECIP', rd['precip']['precip_summary'])
                    if v == None or v == "None":
                        v = "0"
                    n.setDriver('PRECIP', round(float(v), prec), True, force, wmap.uom('PRECIP'))
                else:
                    n.setDriver('PRECIP', 0, True, force, wmap.uom('PRECIP'))
            else:
                n.setDriver('PRECIP', 0, True, force, wmap.uom('PRECIP'))
                
        except Exception as e:
            LOGGER.error('Precipitation summary update failure: {}'.format(e))
            #update('PRECIP', precipitation)
                

    # is forecast days a parameter here or a class variable set at __init__?
    def query_forecasts(self, units, force):
        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        wmap = WeatherData(units)
        prec = 1
        try:
            jdata = self._get_weather_data('forecasts')
            if jdata == None:
                LOGGER.error('Current condition query returned no data')
                return

            # Records are for each day, midnight to midnight
            day = 0
            if 'periods' in jdata['response'][0]:
                LOGGER.debug('Processing periods: %d' % len(jdata['response'][0]['periods']))
                for forecast in jdata['response'][0]['periods']:
                    address = 'forecast_' + str(day)
                    LOGGER.debug(' >>>>   period ' + forecast['dateTimeISO'] + '  ' + address)
                    epoch = int(forecast['timestamp'])
                    n = self.poly.getNode(address)
                    for drv in n.drivers:
                        if drv['driver'] == 'ETO':  # etO, calculated value
                            continue

                        if drv['driver'] == 'GV19':  # day of week
                            dow = time.strftime("%w", time.gmtime(epoch))
                            n.setDriver(drv['driver'], dow, True, force, wmap.uom(drv['driver']))
                            continue

                        try:
                            v = wmap.fparse(drv['driver'], forecast)
                            if v == None or v == "None":
                                v = "0"
                            if drv['driver'] == 'GV15' and wmap.isMetric:
                                v = v * 10 # snow depth is in cm, convert to mm
                            n.setDriver(drv['driver'], round(float(v), prec), True, force, wmap.uom(drv['driver']))
                            LOGGER.debug('setDriver (%s, %f)' %(drv['driver'], float(v)))
                        except Exception as e:
                            LOGGER.warning('Error updating {}: {}'.format(drv['driver'], e))

                    n.max_humidity = float(forecast['maxHumidity'])
                    n.min_humidity = float(forecast['minHumidity'])
                    n.set_ETo(epoch, self.latitude, force)
                    #n.update_forecast(forecast, self.latitude, self.tag, force)
                    day += 1
                    if day >= int(self.days):
                        return

        except Exception as e:
            LOGGER.error('Forecast data failure: {}'.format(e))

