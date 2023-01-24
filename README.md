
# AERIS weather service

This is a node server to pull weather data from the AERIS weather network and make it available to a [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V3](https://github.com/UniversalDevicesInc/pg3)

(c) 2020,2021 Robert Paauwe
MIT license.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server per configuration section below.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the AERIS weather service for current condition data (in seconds). Note that the PWS partner plan only allows for 1000 requests per day so set this appropriately. Also note that two queries are made during each poll.
#### Long Poll
   * How often to poll the AERIS weather service for forecast data (in seconds). Note that the data is only updated every 15 minutes. Setting this to less may result in exceeding the free service rate limit.
#### ClientID
	* Your AERIS client ID, needed to authorize the connection the the AERIS API.
#### ClientSecret
	* Your AERIS client secret key, needed to authorize the connection the the AERIS API.
#### Location
	* Specify the location to use in the weather data queries.  The location can be specified using the following conventions:
		- coordinates (latitude,longitude)  Ex.  37.25,-122.25
		- city,state                        Ex.  seattle,wa
		- city,state,country                Ex.  seattle,wa,us
		- city,country                      Ex.  paris,france
		- zip/postal code                   Ex.  98109
		- 3 character IATA airport codes    Ex.  ROA
		- NOAA public weather zone          Ex.  MNZ029
		- PWS Station                       Ex.  PWS_VILLONWMR2
#### Elevation
	* The elevation of your location, in meters. This is used for the ETo calculation.
#### Forecast Days
	* The number of days of forecast data to track (0 - 12). Note that the basic plan only provides 7 days of data.
#### Plant Type
	* Used for the ETo calculation to compensate for different types of ground cover. Default is 0.23
#### Units
	* set to 'imperial' or 'metric' to control which units are used to display the weather data.

## Node substitution variables
### Current condition node
 * sys.node.[address].ST      (Node sever online)
 * sys.node.[address].CLITEMP (current temperature)
 * sys.node.[address].CLIHUM  (current humidity)
 * sys.node.[address].DEWPT   (current dew point)
 * sys.node.[address].BARPRES (current barometric pressure)
 * sys.node.[address].SPEED   (current wind speed)
 * sys.node.[address].WINDDIR (current wind direction )
 * sys.node.[address].DISTANC (current visibility)
 * sys.node.[address].SOLRAD  (current solar radiation)
 * sys.node.[address].UV      (current uv index)
 * sys.node.[address].GUST    (current gust speed)
 * sys.node.[address].PRECIP  (current precipitation accumulation)
 * sys.node.[address].HEATIX  (current heat index temperature)
 * sys.node.[address].WINDCH  (current wind chill temperature)
 * sys.node.[address].GV2     (current feels like temperature)
 * sys.node.[address].GV11    (current condition coverage)
 * sys.node.[address].GV12    (current intensity of conditions)
 * sys.node.[address].GV13    (current weather conditions)
 * sys.node.[address].GV14    (current percent cloud coverage)
 * sys.node.[address].GV15    (current snow depth)

### Forecast node
 * sys.node.[address].CLIHUM  (forecasted humidity)
 * sys.node.[address].BARPRES (forecasted barometric pressure)
 * sys.node.[address].UV      (forecasted max UV index)
 * sys.node.[address].SPEED   (forecasted wind speed)
 * sys.node.[address].GUST    (forecasted gust speed)
 * sys.node.[address].PRECIP  (forecasted precipitation)
 * sys.node.[address].POP     (forecasted precent chance of precipitation)
 * sys.node.[address].ETO     (calculated ETo for the day)
 * sys.node.[address].GV19    (day of week forecast is for)
 * sys.node.[address].GV0     (forecasted high temperature)
 * sys.node.[address].GV1     (forecasted low temperature)
 * sys.node.[address].GV7     (forecasted max wind speed)
 * sys.node.[address].GV8     (forecasted min wind speed)
 * sys.node.[address].GV11    (forecasted condition coverage)
 * sys.node.[address].GV12    (forecasted intensity of conditions)
 * sys.node.[address].GV13    (forecasted weather conditions)
 * sys.node.[address].GV14    (forecasted percent cloud coverage)
 * sys.node.[address].GV15    (forecasted snowfall)

## Requirements
1. Polyglot V3.
2. ISY firmware 5.3.x or later
3. An account with AERIS weather (http://aerisweather.com)


- 2.0.6 04/23/2022
   - fix typo HEADIX should be HEATIX
- 2.0.5 07/20/2021
   - Stop generating a warning for ST
- 2.0.4 07/20/2021
   - Fix units for precipitation
- 2.0.3 07/15/2021
   - Fix parameter handling so that it works with latest udi_interface.
- 2.0.1 02/17/2021
   - Change notification fuctions to use subscribe (interface change)
- 2.0.0 01/26/2021
   - Re-write to work with Polyglot version 3
   - Make use of new status values related to weather and minimize use of
     general purpose variables.
- 1.0.13 12/12/2020
   - Update forecast limit to match Aeris change.
- 1.0.12 10/02/2020
   - Update NLS profile file with typo fix and intensity fix.
- 1.0.11 08/25/2020
   - Update polling interval documentation
   - Fix typo in MPH to m/s conversion function
   - Update polling interval to not exceed free plan limits
- 1.0.10 07/19/2020
   - Correct latitude parsing and add error checking.
- 1.0.9 07/18/2020
   - Add kph2ms function to convert windspeed for ETo calculation
   - Fix condition so that the conversion needed when not metric are correct.
   - Add update latitude data from current observation data.
- 1.0.8 07/18/2020
   - Fix UOM for windspeed. Metric UOM is KPH, not M/S.
   - Update temperature range for celcius to go lower.
   - Fix error when Aeris data is different than originally expected.
- 1.0.7 06/17/2020
   - update editor for ETo to include inches/day
- 1.0.6 04/16/2020
   - fix syntax error introduced with previous change
- 1.0.5 04/16/2020
   - snowfall in inches incorrectly was multiplied by 10.
- 1.0.4 04/07/2020
   - Handle precipitation summary response if it's either a list or dictionary
- 1.0.3 04/07/2020
   - Add query to get preciptitation summary info
- 1.0.2 03/30/2020
   - Add snow depth to current conditions and forecasts
   - change "rain today" to "precipitation"
- 1.0.1 03/30/2020
   - Fix issues with the profile files.
- 1.0.0 03/18/2020
   - Initial public release
- 0.0.1 08/20/2019
   - Initial version published to github for testing
