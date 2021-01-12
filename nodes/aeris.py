#!/usr/bin/env python3
"""
Polyglot v3 node server AERIS weather data
Copyright (C) 2019,2020,2021 Robert Paauwe
"""

import udi_interface
import sys
import time
import datetime
import requests
import socket
import math
import re
import json
import node_funcs
from nodes import aeris_daily
from nodes import uom
from nodes import weather_codes as wx
from nodes import query

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(udi_interface.Node):
    id = 'weather'
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)

        self.poly = polyglot    # redundent
        self.name = name        # redundent
        self.address = address  # redundent
        self.primary = primary  # redundent
        self.configured = False
        self.private = 'My controller private info'
        #self.latitude = 0
        #self.longitude = 0
        self.force = True
        #self.tag = {}
        self.node_added_count = 0
        self.Notices = Custom(polyglot, 'notices')
        self.Parameters = Custom(polyglot, 'customparams')

        self.params = node_funcs.NSParameters([{
            'name': 'ClientID',
            'default': 'set me',
            'isRequired': True,
            'notice': 'AERIS Client ID must be set',
            },
            {
            'name': 'ClientSecret',
            'default': 'set me',
            'isRequired': True,
            'notice': 'AERIS Client Secret must be set',
            },
            {
            'name': 'Location',
            'default': 'set me',
            'isRequired': True,
            'notice': 'AERIS location must be set',
            },
            {
             'name': 'Units',
            'default': 'imperial',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Forecast Days',
            'default': '0',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Elevation',
            'default': '0',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Plant Type',
            'default': '0.23',
            'isRequired': False,
            'notice': '',
            },
            ])

        self.q = query.queries(self.poly)

        self.poly.onConfig(self.configHandler)
        self.poly.onCustomParams(self.parameterHandler)
        self.poly.onStart(self.address, self.start)
        self.poly.onPoll(self.poll)
        self.poly.onAddNodeDone(self.nodeHandler)

        self.poly.addNode(self)

    # Process changes to customParameters
    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.params.update(self.Parameters)

        self.q.units = self.params.get('Units')
        self.q.location = self.params.get('Location')
        self.q.client_id = self.params.get('ClientID')
        self.q.client_secret = self.params.get('ClientSecret')
        self.q.plant_type = self.params.get('Plant Type')
        self.q.days = self.params.get('Forecast Days')
        self.q.elevation = self.params.get('Elevation')

        if self.params.isConfigured():
            self.Notices.clear()
            self.configured = True
            # check if number of forecast days has changed
            if self.params.isSet('Forecast Days') and self.Parameters.isChanged('Forecast Days'):
                LOGGER.critical('CALLING DISCOVERY from parameter Handler')
                self.discover()

    def configHandler(self, config):
        LOGGER.info('handle config = {}'.format(config))

    def nodeHandler(self, data):
        self.node_added_count += 1

        # testing...
        LOGGER.debug('Handling node add done for {}'.format(data.get('address')))
        LOGGER.debug('******************  node private = {}'.format(data.get('private')))


    def start(self):
        LOGGER.info('Starting node server')
        self.check_params()
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        #self.set_tags(self.params.get('Units'))

        LOGGER.critical('CALLING DISCOVERY from start')
        self.discover()

        # Do an initial query to get filled in as soon as possible
        if self.configured:
            self.q.configured = True
            self.q.query_conditions(self.address, self.params.get('Units'), self.force)
            self.q.query_forecasts(self.params.get('Units'), self.force)
            self.force = False

        LOGGER.info('Node server started')

    def poll(self, longpoll):
        if longpoll:
            self.q.query_forecasts(self.params.get('Units'), self.force)
        else:
            self.q.query_conditions(self.address, self.params.get('Units'), self.force)

    def query(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create any additional nodes here
        LOGGER.info("In Discovery...")

        node_count = 0
        num_days = int(self.params.get('Forecast Days'))
        if num_days < 7:
            # delete any extra days
            for day in range(num_days, 7):
                address = 'forecast_' + str(day)
                try:
                    self.delNode(address)
                except:
                    LOGGER.debug('Failed to delete node ' + address)

        nodes = self.poly.getNodes()
        for day in range(0,num_days):
            address = 'forecast_' + str(day)
            title = 'Forecast ' + str(day)
            if address not in nodes:
                try:
                    LOGGER.info('Creating forecast node {} {}'.format(address,title))
                    node = aeris_daily.DailyNode(self.poly, self.address, address, title, self.params.get('Units'))
                    node.private = 'private data for ' + address
                    node.plant_type = self.params.get('Plant Type')
                    node.elevation = self.params.get('Elevation')
                    node_count += 1
                    LOGGER.debug('Adding forecast node {}'.format(title))
                    self.poly.addNode(node)
                except Exception as e:
                    LOGGER.error('Failed to create forecast node ' + title)
                    LOGGER.error('  -> {}'.format(e))
            else:
                LOGGER.debug('Forecast node {} already exist.'.format(address))

        # wait for all nodes to be added before continuing
        while self.node_added_count < (1 + node_count):
            time.sleep(2)


    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def check_params(self):
        self.Notices.clear()

        if self.params.isConfigured():
            LOGGER.debug('All required parameters are set!')
            self.configured = True
            if int(self.params.get('Forecast Days')) > 6:
                # TODO: Set a notice: 'Number of days of forecast data is limited to 6 days'
                self.params.set('Forecast Days', 6)
        else:
            LOGGER.info('User configuration required.')
            self.Notices.load(self.params.activeNotices(), True)

        self.params.save(self.Parameters)

    # Set the uom dictionary based on current user units preference
    def set_driver_uom(self, units):
        LOGGER.info('Configure driver units to ' + units)
        self.uom = uom.get_uom(units)

        # Need to figure out how to get access to the nodes.  Should I
        # be tracking the child nodes or can we get the list from the
        # interface?
        LOGGER.error('Getnodes returns {}'.format(self.poly.getNodes()))
        nodes = self.poly.getNodes()
        for node in nodes:
            LOGGER.error('Checking for non-controller node {}'.format(node))
            if node != "controller":
                LOGGER.error('Setting uom for node {}'.format(node))
                nodes[node].set_driver_uom(units)

    def remove_notices_all(self, command):
        self.Notices.clear()

    commands = {
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'QUERY': query,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'CLITEMP', 'value': 0, 'uom': 4},   # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'DEWPT', 'value': 0, 'uom': 4},     # dewpoint
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'WINDDIR', 'value': 0, 'uom': 76},  # direction
            {'driver': 'SPEED', 'value': 0, 'uom': 32},    # wind speed
            {'driver': 'GV5', 'value': 0, 'uom': 32},      # gust speed
            {'driver': 'GV2', 'value': 0, 'uom': 4},       # feels like
            {'driver': 'GV3', 'value': 0, 'uom': 4},       # heat index
            {'driver': 'GV4', 'value': 0, 'uom': 4},       # wind chill
            {'driver': 'GV6', 'value': 0, 'uom': 82},      # rain
            {'driver': 'GV15', 'value': 0, 'uom': 82},     # snow depth
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # climate coverage
            {'driver': 'GV12', 'value': 0, 'uom': 25},     # climate intensity
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # climate conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # cloud conditions
            {'driver': 'DISTANC', 'value': 0, 'uom': 83},  # visibility
            {'driver': 'SOLRAD', 'value': 0, 'uom': 74},   # solar radiataion
            {'driver': 'UV', 'value': 0, 'uom': 71},       # uv index
            {'driver': 'GVP', 'value': 30, 'uom': 25},     # log level
            ]


