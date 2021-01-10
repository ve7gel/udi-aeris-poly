"""
Do I want this encapsulated in a class or not?

export:
    query_conditions(update_function, force)
    query_forecasts(force)

"""
import udi_interface
import requests
from nodes import weather_codes as wx

LOGGER = udi_interface.LOGGER

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
        if key == 'units':
            self._initialize_tags(value)

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

    def query_conditions(self, update, force):
        # Query for the current conditions. We can do this fairly
        # frequently, probably as often as once a minute.

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        precipitation = 0

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

            # why are we useing self.tag mapping here?
            update('CLITEMP', ob[self.tag['temperature']])
            update('CLIHUM', ob[self.tag['humidity']])
            update('BARPRES', ob[self.tag['pressure']])
            update('SPEED', ob[self.tag['windspeed']])
            update('GV5', ob[self.tag['gustspeed']])
            update('WINDDIR', ob[self.tag['winddir']])
            update('DISTANC', ob[self.tag['visibility']])
            update('DEWPT', ob[self.tag['dewpoint']])
            update('GV3', ob[self.tag['heatindex']])
            update('GV4', ob[self.tag['windchill']])
            update('GV2', ob[self.tag['feelslike']])
            update('SOLRAD', ob[self.tag['solarrad']])
            update('UV', ob[self.tag['uv']])
            update('GV15', ob[self.tag['snow']])
            # Weather conditions:
            #  ob['weather']
            #  ob['weatherShort']
            #  ob['weatherCoded']
            #    [coverage] : [intensity] : [weather]
            #     -- these can be mapped to strings

            LOGGER.debug('**>>> WeatherCoded = ' + ob['weatherCoded']);
            weather = ob['weatherCoded'].split(':')[0]
            update('GV11', wx.coverage_codes(weather))
            weather = ob['weatherCoded'].split(':')[1]
            update('GV12', wx.intensity_codes(weather))
            weather = ob['weatherCoded'].split(':')[2]
            LOGGER.debug('>>>  weather = ' + weather)
            update('GV13', wx.weather_codes(weather))
            LOGGER.debug('>>>  Setting GV13 to ' + str(wx.weather_codes(weather)))

            # cloud cover
            #  ob['cloudsCoded'] ??
            update('GV14', ob['sky'])

            # precipitation
            precipitation = ob[self.tag['precipitation']]

            '''
            TODO:
            - weather
            - snow depth
            - ceiling
            - light
            '''

        except Exception as e:
            LOGGER.error('Current observation update failure: {}'.format(e))

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
                LOGGER.debug('Setting precipitation to: ' + str(rd['precip'][self.tag['precip_summary']]))
                update('GV6', rd['precip'][self.tag['precip_summary']])
        except Exception as e:
            LOGGER.error('Precipitation summary update failure: {}'.format(e))
            update('GV6', precipitation)
                

    # is forecast days a parameter here or a class variable set at __init__?
    def query_forecasts(self, force):
        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

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
                    n = self.poly.getNode(address)
                    n.update_forecast(forecast, self.latitude, self.elevation, self.plant_type, self.tag, force)
                    day += 1
                    if day >= int(self.days):
                        return

        except Exception as e:
            LOGGER.error('Forecast data failure: {}'.format(e))

    """
    We use a mapping here because the tags we want out of the responses are different
    depending on the units selected by the user.
    """
    def _initialize_tags(self, units):
        if units == 'metric':
            self.tag['temperature'] = 'tempC'
            self.tag['humidity'] = 'humidity'
            self.tag['pressure'] = 'pressureMB'
            self.tag['windspeed'] = 'windSpeedKPH'
            self.tag['gustspeed'] = 'windGustKPH'
            self.tag['winddir'] = 'windDirDEG'
            self.tag['visibility'] = 'visibilityKM'
            self.tag['precipitation'] = 'precipMM'
            self.tag['snow'] = 'snowDepthCM'
            self.tag['snowf'] = 'snowCM'
            self.tag['dewpoint'] = 'dewpointC'
            self.tag['heatindex'] = 'heatindexC'
            self.tag['windchill'] = 'windchillC'
            self.tag['feelslike'] = 'feelslikeC'
            self.tag['solarrad'] = 'solradWM2'
            self.tag['sky'] = 'sky'
            self.tag['temp_min'] = 'minTempC'
            self.tag['temp_max'] = 'maxTempC'
            self.tag['humidity_min'] = 'minHumidity'
            self.tag['humidity_max'] = 'maxHumidity'
            self.tag['wind_min'] = 'windSpeedMinKPH'
            self.tag['wind_max'] = 'windSpeedMaxKPH'
            self.tag['winddir_min'] = 'windDirMinDEG'
            self.tag['winddir_max'] = 'windDirMaxDEG'
            self.tag['uv'] = 'uvi'
            self.tag['pop'] = 'pop'
            self.tag['timestamp'] = 'timestamp'
            self.tag['precip_summary'] = 'totalMM'
        else:
            self.tag['temperature'] = 'tempF'
            self.tag['humidity'] = 'humidity'
            self.tag['pressure'] = 'pressureIN'
            self.tag['windspeed'] = 'windSpeedMPH'
            self.tag['gustspeed'] = 'windGustMPH'
            self.tag['winddir'] = 'windDirDEG'
            self.tag['visibility'] = 'visibilityMI'
            self.tag['precipitation'] = 'precipIN'
            self.tag['snow'] = 'snowDepthIN'
            self.tag['snowf'] = 'snowIN'
            self.tag['dewpoint'] = 'dewpointF'
            self.tag['heatindex'] = 'heatindexF'
            self.tag['windchill'] = 'windchillF'
            self.tag['feelslike'] = 'feelslikeF'
            self.tag['solarrad'] = 'solradWM2'
            self.tag['sky'] = 'sky'
            self.tag['temp_min'] = 'minTempF'
            self.tag['temp_max'] = 'maxTempF'
            self.tag['humidity_min'] = 'minHumidity'
            self.tag['humidity_max'] = 'maxHumidity'
            self.tag['wind_min'] = 'windSpeedMinMPH'
            self.tag['wind_max'] = 'windSpeedMaxMPH'
            self.tag['winddir_min'] = 'windDirMinDEG'
            self.tag['winddir_max'] = 'windDirMaxDEG'
            self.tag['uv'] = 'uvi'
            self.tag['pop'] = 'pop'
            self.tag['timestamp'] = 'timestamp'
            self.tag['precip_summary'] = 'totalIN'
