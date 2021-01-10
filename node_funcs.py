#
#  Common functions used by nodes


import udi_interface

LOGGER = udi_interface.LOGGER

"""
    Some common functions to be used by node servers

    To add these functions call the add_functions_as_methods()
    function.  Then the functions specified in 'functions' below
    will be available for use as if they were defined in the node's
    primary class.
"""
def add_functions_as_methods(functions):
    def decorator(Class):
        for function in functions:
            setattr(Class, function.__name__, function)
        return Class
    return decorator


# Wrap all the setDriver calls so that we can check that the 
# value exist first.
def update_driver(self, driver, value, force=False, prec=3):
    try:
        if value == None or value == "None":
            value = "0"
        self.setDriver(driver, round(float(value), prec), True, force, self.uom[driver])
        LOGGER.debug('setDriver (%s, %f)' %(driver, float(value)))
    except Exception as e:
        LOGGER.warning('Error updating {}: {}'.format(driver, e))

functions = (update_driver,)

"""
    Functions to handle custom parameters.

    pass in a list of name and default value parameters
    [
        {'name': name of parameter,
         'default': default value of parameter,
         'notice': 'string to send notice if not set',
         'isRequired: True/False,
        },
        {'name': name of parameter,
         'default': default value of parameter,
         'notice': 'string to send notice if not set',
         'isRequired: True/False,
        },
    ]

    usage:
       self.params = NSParameters(param_list)
       self.params.get('param1')
       if self.params.isSet('param1'):

"""

class NSParameters:
    def __init__(self, parameters):
        self.internal = []

        for p in parameters:
            self.internal.append({
                'name': p['name'],
                'value': '', 
                'default': p['default'],
                'isSet': False,
                'isRequired': p['isRequired'],
                'notice_msg': p['notice'],
                })

    def set(self, name, value):
        for p in self.internal:
            if p['name'] == name:
                p['value'] = value
                if value != p['default']:
                    p['isSet'] = True
                else:
                    p['isSet'] = False
                return

    def get(self, name):
        for p in self.internal:
            if p['name'] == name:
                if p['isSet']:
                    return p['value']
                else:
                    return p['default']

    def isSet(self, name):
        for p in self.internal:
            if p['name'] == name:
                return p['isSet']
        return False

    def exists(self, name):
        for p in self.internal:
            if p['name'] == name:
                return True
        return False

    def activeNotices(self):
        notices = {}
        for p in self.internal:
            if not p['isSet'] and p['isRequired']:
                notices[p['name']] = p['notice_msg']
        return notices

    def update(self, params):
        for pkey in params.keys():
            old_value = self.get(pkey)
            if old_value is None:
                # create new entry in internal, user added
                self.internal.append({
                    'name': pkey,
                    'value': params[pkey],
                    'default': '',
                    'isSet': True,
                    'isRequired': False,
                    'notice_msg': ''
                    })
            elif old_value != params[pkey]:
                self.set(pkey, params[pkey])

    def isConfigured(self):
        for p in self.internal:
            if not p['isSet'] and p['isRequired']:
                LOGGER.debug('Returning false, not all required parameters are set.')
                return False
        LOGGER.debug('Returning true, all required parameters are set.')
        return True

    def save(self, params):
        for p in self.internal:
            if p['isSet']:
                params[p['name']] = p['value']
            else:
                params[p['name']] = p['default']


