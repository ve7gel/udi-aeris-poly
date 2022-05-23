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
#import node_funcs
from nodes import aeris_daily
from nodes import query

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class Controller(udi_interface.Node):
    id = 'weather'
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)

        self.poly = polyglot
        self.name = name
        self.address = address
        self.primary = primary
        self.configured = False
        self.node_added_count = 0

        self.Notices = Custom(polyglot, 'notices')
        self.Parameters = Custom(polyglot, 'customparams')

        self.q = query.queries(self.poly)

        self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.nodeHandler)

        self.poly.ready()
        self.poly.addNode(self)

    # Process changes to customParameters
    def parameterHandler(self, params):
        validCli = False
        validSec = False
        validLoc = False
        self.Parameters.load(params)
        #self.params.update(self.Parameters)

        if self.Parameters['ClientID'] is not None:
            if len(self.Parameters['ClientID']) == 21:
                validCli = True
            else:
                LOGGER.debug('Client ID {} invalid.'.format(self.Parameters['ClientID']))
        else:
            LOGGER.error('Client ID is missing.')

        if self.Parameters['ClientSecret'] is not None:
            if len(self.Parameters['ClientSecret']) == 40:
                validSec = True
            else:
                LOGGER.debug('Client Secret {} invalid.'.format(self.Parameters['ClientSecret']))
        else:
            LOGGER.error('Client Secret is missing.')

        if self.Parameters['Location'] is not None:
            if 'PWS' in self.Parameters['Location']:
                validLoc = True
            elif len(self.Parameters['Location']) > 2:
                validLoc = True
            else:
                LOGGER.debug('Location {} invalid.'.format(self.Parameters['Location']))
        else:
            LOGGER.error('Client Secret is missing.')


        self.Notices.clear()

        if validCli and validSec and validLoc:
            self.q.units = self.Parameters['Units']
            self.q.location = self.Parameters['Location']
            self.q.client_id = self.Parameters['ClientID']
            self.q.client_secret = self.Parameters['ClientSecret']
            self.q.plant_type = self.Parameters['Plant Type']
            self.q.days = self.Parameters['Forecast Days']
            self.q.elevation = self.Parameters['Elevation']
            self.q.configured = True
            self.configured = True

            # check if number of forecast days has changed
            if self.Parameters.isChanged('Forecast Days'):
                LOGGER.info('CALLING DISCOVERY from parameter Handler')
                self.discover()
                self.q.query_forecasts(self.Parameters['Units'], True)
        else:
            if not validCli:
                LOGGER.warning('Client ID must be set')
                self.Notices['id'] = 'AERIS client ID must be configured.'
            if not validSec:
                LOGGER.warning('Client secret must be set')
                self.Notices['secret'] = 'AERIS client secret key must be configured.'
            if not validLoc:
                LOGGER.warning('Location must be set')
                self.Notices['loc'] = 'AERIS location must be configured.'

    def configHandler(self, config):
        # at this time the interface should have all the nodes
        # included from the database.  Here's where we could 
        # loop through those and create wrapped versions.
        #LOGGER.info('handle config = {}'.format(config))
        nodes = self.poly.getNodes()
        for n in nodes:
            LOGGER.info('Found node {} = {}'.format(n, nodes[n]))

    def nodeHandler(self, data):
        self.node_added_count += 1

    def start(self):
        LOGGER.info('Starting node server')
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()

        while not self.configured:
            time.sleep(10)

        LOGGER.critical('CALLING DISCOVERY from start')
        self.discover()

        # Do an initial query to get filled in as soon as possible
        self.q.query_conditions(self.address, self.Parameters['Units'], True)
        self.q.query_forecasts(self.Parameters['Units'], True)

        LOGGER.info('Node server started')

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            self.q.query_conditions(self.address, self.Parameters['Units'], False)
        else:
            self.q.query_forecasts(self.address, self.Parameters['Units'], False)

    def query(self):
        self.q.query_conditions(self.address, self.Parameters['Units'], True)
        self.q.query_forecasts(self.Parameters['Units'], True)

    def discover(self, *args, **kwargs):
        # Create any additional nodes here
        LOGGER.info("In Discovery...")

        node_count = 1
        num_days = int(self.Parameters['Forecast Days'])
        if num_days < 7:
            # delete any extra days
            for day in range(num_days, 7):
                address = 'forecast_' + str(day)
                try:
                    if self.poly.getNode(address):
                        self.poly.delNode(address)
                except:
                    LOGGER.debug('Failed to delete node ' + address)

        for day in range(0,num_days):
            address = 'forecast_' + str(day)
            title = 'Forecast ' + str(day)
            try:
                if self.poly.getNode(address) is None:
                    LOGGER.info('Creating forecast node {} {}'.format(address,title))
                    node = aeris_daily.DailyNode(self.poly, self.address, address, title, self.Parameters['Units'])
                    node.private = 'private data for ' + address
                    node.plant_type = self.Parameters['Plant Type']
                    node.elevation = self.Parameters['Elevation']

                    LOGGER.debug('Adding forecast node {}'.format(title))
                    node_count += 1
                    self.poly.addNode(node)

                    # Wait for node to be created
                    while self.node_added_count < node_count:
                        time.sleep(2)
                else:
                    node_count += 1
                    LOGGER.info('Node {} already exists, skipping'.format(address))

            except Exception as e:
                LOGGER.error('Failed to create forecast node {}: {}'.format(address, e))
                LOGGER.error('  -> {}'.format(e))


    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

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
            {'driver': 'GUST', 'value': 0, 'uom': 32},     # gust speed
            {'driver': 'GV2', 'value': 0, 'uom': 4},       # feels like
            {'driver': 'HEATIX', 'value': 0, 'uom': 4},    # heat index
            {'driver': 'WINDCH', 'value': 0, 'uom': 4},    # wind chill
            {'driver': 'PRECIP', 'value': 0, 'uom': 82},   # rain
            {'driver': 'GV15', 'value': 0, 'uom': 82},     # snow depth
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # climate coverage
            {'driver': 'GV12', 'value': 0, 'uom': 25},     # climate intensity
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # climate conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # cloud conditions
            {'driver': 'DISTANC', 'value': 0, 'uom': 83},  # visibility
            {'driver': 'SOLRAD', 'value': 0, 'uom': 74},   # solar radiataion
            {'driver': 'UV', 'value': 0, 'uom': 71},       # uv index
            ]


