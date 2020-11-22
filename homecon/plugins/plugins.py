#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from homecon.core.database import get_database, Field
from homecon.core.plugins.plugin import Plugin

from homecon.plugins.states import States
from homecon.plugins.websocket import Websocket
from homecon.plugins.pages import Pages
from homecon.plugins.alarms.scheduler import Scheduler
from homecon.plugins.knx import Knx


logger = logging.getLogger(__name__)


def get_plugins_table():
    db = get_database()
    if 'plugins' in db:
        table = db.plugins
    else:
        table = db.define_table(
            'plugins',
            Field('name', type='string', default='', unique=True),
            Field('string', type='string', default=''),
            Field('package', type='string'),
            Field('active', type='boolean'),
        )
    return table


class Plugins(Plugin):
    """
    A class to manage plugins dynamically
    """
    def __init__(self):
        super().__init__()
        self._plugin_folder = 'plugins'
        self._core_plugins = {
            'plugins': self,
            'states': States(),
            'websocket': Websocket(),
            'pages': Pages(),
            'scheduler': Scheduler(),
            'knx': Knx()
        }
        self._active_plugins = {}

        # initialize plugins
        db_entries = get_database()(get_plugins_table()).select()
        for db_entry in db_entries:
            if db_entry['active']:
                plugin_class = self._import(db_entry['name'], db_entry['package'])
                self._active_plugins[db_entry['name']] = plugin_class()

    def initialize(self):
        logger.debug('Plugins plugin initialized')

    def get_available_plugins_list(self):
        """
        Generate a list of all available optional plugins and those that are active
        
        """
        db_entries = get_database()(get_plugins_table()).select()
        plugins = []
        for db_entry in db_entries:
            plugins.append({'name': db_entry['name'], 'info': db_entry['info'], 'active': db_entry['active']})
        return plugins

    def get_active_plugins_list(self):
        """
        Generate a list of all active plugins, excluding core plugins
        """
        return sorted([key for key in self._active_plugins.keys()])

    def activate(self, name):
        """
        Activate an available plugin by name

        """
        db_entries = get_plugins_table().get(name=name)
        if len(db_entries) == 1:
            db_entry = db_entries[0]
            plugin_class = self._import(name, package=db_entry['package'])
            if plugin_class is not None:
                self._active_plugins[name] = plugin_class()
                self._active_plugins[name].start()
                get_plugins_table().put(active=True, where='id=\'{}\''.format(db_entry['id']))
                logger.debug("plugin {} activated".format(name))

    def deactivate(self, name):
       pass

    def install(self, url):
        logging.debug('installing plugin from'.format(url))

    def _import(self, name, package=None):
        """
        Imports a plugin module

        this attempts to load the plugin with the correct format by name from
        the plugins folder

        Parameters
        ----------
        name: string
            The module name of the plugin

        package: string
            Package where to find the plugin, defaults to the default _plugin_folder

        returns
        -------
        pluginclass: class
            The plugin class if defined in the module otherwise ``None``

        """

        if package is None or package == '':
            plugin_module = __import__(name, fromlist=[name])
        else:
            plugin_module = __import__('{}.{}'.format(package, name), fromlist=[name])

        plugin_class = None
        plugin_class_name = name.capitalize()
        if plugin_class_name in dir(plugin_module):
            plugin_class = getattr(plugin_module, plugin_class_name)
        return plugin_class

    def listen_plugins_settings(self, event):
        sections = []
        for key, plugin in self.items():
            section = plugin.settings_sections
            if section is not None:
                sections += section

        event.reply({'plugin': event.data['plugin'], 'value': sections})

    # def get_state_config_keys(self):
    #
    #     keyslist = []
    #
    #     keyslist.append({'name': 'states', 'keys': ['type', 'quantity', 'unit', 'label', 'description']})
    #     keyslist.append({'name': 'permissions', 'keys': ['readusers', 'writeusers', 'readgroups', 'writegroups']})
    #
    #     for name,plugin in core.plugins.items():
    #         keys = plugin.config_keys
    #         if len(config)>0:
    #             keyslist.append({'name':name, 'keys':keys})
    #
    #     return keyslist
    #
    # def get_components(self):
    #
    #     keyslist = []
    #
    #     keyslist.append({'name':'building', 'components':[
    #         {
    #             'name': 'relay',
    #             'states': [
    #                 'value',
    #             ]
    #         },
    #     ]})
    #
    #     #for name,plugin in self._plugins.items():
    #     #    keys = plugin.components()
    #     #    if len(config)>0:
    #     #        keyslist.append({'name':name, 'keys':keys})
    #
    #     return keyslist
    #
    # def listen_list_optionalplugins(self,event):
    #     core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])
    #
    # def listen_list_activeplugins(self,event):
    #     core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])
    #
    # def listen_list_state_config_keys(self,event):
    #     core.websocket.send({'event':'list_state_config_keys', 'path':'', 'value':self.get_state_config_keys()}, clients=[event.client])
    #
    # def listen_activate_plugin(self,event):
    #     self.activate(event.data['plugin'])
    #     core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client]) # FIXME should all clients be notified of plugin changes?
    #     core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])
    #     core.event.fire('component_types',{},client=event.client)
    #
    # def listen_deactivate_plugin(self,event):
    #     self.deactivate(event.data['plugin'])
    #     core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])
    #     core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])
    #     #FIXME components defined in a plugin should be unregisterd and component instances deleted from the active list
    #     core.event.fire('component_types',{},client=event.client)
    #
    # def listen_install_plugin(self,event):
    #     if self.install(event.data['url']):
    #         core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])
    #         core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])

    def __getitem__(self,path):
        return None

    def __iter__(self):
        return iter([])

    def __contains__(self,path):
        return False

    def keys(self):
        plugins = {}
        for key, val in self._core_plugins.values():
            plugins[key] = val
        for key, val in self._active_plugins.values():
            plugins[key] = val
        return plugins.keys()

    def items(self):
        plugins = {}
        for key, val in self._core_plugins.items():
            plugins[key] = val
        for key, val in self._active_plugins.items():
            plugins[key] = val
        return plugins.items()

    def values(self):
        plugins = {}
        for key, val in self._core_plugins.items():
            plugins[key] = val
        for key, val in self._active_plugins.items():
            plugins[key] = val
        return plugins.values()
