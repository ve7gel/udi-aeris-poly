# Node definition for a daily forecast node

import udi_interface
import json
import time
import datetime
from nodes import et3
from nodes import query
import node_funcs

LOGGER = udi_interface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class DailyNode(udi_interface.Node):
    id = 'daily'
    private = 'This is my private info'
    # TODO: add wind speed min/max, pop, winddir min/max
    drivers = [
            {'driver': 'GV19', 'value': 0, 'uom': 25},     # day of week
            {'driver': 'GV0', 'value': 0, 'uom': 4},       # high temp
            {'driver': 'GV1', 'value': 0, 'uom': 4},       # low temp
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # coverage
            {'driver': 'GV12', 'value': 0, 'uom': 25},     # intensity
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # weather
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # clouds
            {'driver': 'SPEED', 'value': 0, 'uom': 32},    # wind speed
            {'driver': 'GV5', 'value': 0, 'uom': 32},      # gust speed
            {'driver': 'GV6', 'value': 0, 'uom': 82},      # precipitation
            {'driver': 'GV15', 'value': 0, 'uom': 82},     # snow depth
            {'driver': 'GV7', 'value': 0, 'uom': 32},      # wind speed max
            {'driver': 'GV8', 'value': 0, 'uom': 32},      # wind speed min
            {'driver': 'GV18', 'value': 0, 'uom': 22},     # pop
            {'driver': 'UV', 'value': 0, 'uom': 71},       # UV index
            {'driver': 'GV20', 'value': 0, 'uom': 106},    # mm/day
            ]

    def __init__(self, polyglot, primary, address, name, units):
        super(DailyNode, self).__init__(polyglot, primary, address, name)

        self.elevation = 0
        self.plant_type = 0.23
        self.units = units
        self.min_humidity = 0
        self.max_humidity = 0

    def mm2inch(self, mm):
        return round(mm/25.4, 2)

    def getDriverValue(self, driver):
        for d in self.drivers:
            if d['driver'] == driver:
                return d['value']
        LOGGER.error('{} not found in drivers array'.format(driver))
        return -1

    """
      Elevation - set at init
      plant type - set at init

      temperature min/max - available from drivers GV1/GV0
      windspeed - available from drivers (SPEED)
      humidity min/max -- ??? In data, but not in drivers
    """

    def set_ETo(self, epoch, latitude, force):
        # Calculate ETo
        #  Temp is in degree C and windspeed is in m/s, we may need to
        #  convert these.
        J = datetime.datetime.fromtimestamp(epoch).timetuple().tm_yday

        Tmin = self.getDriverValue('GV1')
        Tmax = self.getDriverValue('GV0')
        Ws = self.getDriverValue('SPEED')
        if self.units != 'metric':
            LOGGER.info('Conversion of temperature/wind speed required')
            Tmin = et3.FtoC(Tmin)
            Tmax = et3.FtoC(Tmax)
            Ws = et3.mph2ms(Ws)
        else:
            Ws = et3.kph2ms(Ws)

        #et0 = et3.evapotranspriation(Tmax, Tmin, None, Ws, float(self.elevation), self.max_humidity, self.min_humidity, latitude, float(self.plant_type), J)

        et3.tMin = Tmin
        et3.tMax = Tmax
        et3.julianDay = datetime.datetime.fromtimestamp(epoch).timetuple().tm_yday
        et3.windSpeed = Ws
        et3.elevation = float(self.elevation)
        et3.hMin = self.min_humidity
        et3.hMax = self.max_humidity
        et3.latitude = latitude
        et3.plantType = float(self.plant_type)
        et0 = et3.get_et0()

        # et0 is in mm/hr.  If the user wants imperial or uk units, it needs to be converted.
        if self.units == 'imperial' or self.units == 'uk':
            et0 = self.mm2inch(et0)
        
        wmap = query.WeatherData(self.units)
        self.setDriver('GV20', et0, True, force, wmap.uom('GV20'))
        LOGGER.info('ETo = {}'.format(et0))
