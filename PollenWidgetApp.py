# encoding: utf-8

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.properties import DictProperty, ObjectProperty, StringProperty, ListProperty
from kivy.uix.spinner import Spinner
from datetime import datetime
from time import mktime, strptime
import os
from kivy.network.urlrequest import UrlRequest


class PollenWidget(RelativeLayout):
    '''Shows infections for the current date and plots for daily and cumulative infections.

        Attributes:
        The attributes (excluding dataset[]) are bound by name to propertis in the kv file. Updating them will automatically update the displayed data in the visualisation
            statesAndRegions (DictProperty):
                contains federal states and corresponding regions
                {'state 1': ['region 1', 'region 2', ...], 'state 2': ['region 1', 'region 2', ...]}
            states (ListProperty):
                list holding all federal states. Retrieved from statesAndRegions.
            regions (ListProperty):
                list holding all regions of the selected state.
                Retrieved from statesAndRegions
            activeState (StringProperty, str):
                currently active state
            activeRegions (StringProperty, str):
                currently active region
            notification  (StringProperty, str):
                Error string. Shows exceptions, like no data available.
                Initially set to --.
            dataset (list):
                list holding all the downloaded data
    '''

    statesAndRegions = DictProperty({})
    states = ListProperty([])
    regions = ListProperty([])
    activeState = StringProperty('--')
    activeRegion = StringProperty('--')
    notification = StringProperty('')
    dataset = []

    def __init__(self, **kwargs):
        super(PollenWidget, self).__init__(**kwargs)
        pass

    def download_dataset(self, url):
        UrlRequest(url = url, on_success = self.update_dataset)

    def update_dataset(self, request, result):

        self.dataset = result['content']
        self.update_states_spinner()
        
    def update_active_region(self, region, *args, **kwargs):
        '''update all data for a new selected country'''

        self.activeRegion = region

        description = {'-1' : 0,
                       '0' : 0,
                       '0-1' : 0,
                       '1' : 1,
                       '1-2' : 1,
                       '2' : 2,
                       '2-3' : 2,
                       '3' : 3}
        
        color = {'-1' : [0, 1, 1, 1],
                 '0' : [0, 1, 1, 1],
                 '0-1' : [0, 1, 1, 1],
                 '1' : [0, 1, 0, 1],
                 '1-2' : [0, 1, 0, 1],
                 '2' : [0, 1, 0, 1],
                 '2-3' : [0, 1, 0, 1],
                 '3' : [1, 0, 0, 1]}

        #clear all previous added widgets
        self.ids['grid'].clear_widgets()

        for element in self.dataset:
            if element['partregion_name'] == self.activeRegion and element['region_name'] == self.activeState:
                for key, value in element['Pollen'].items():
                    self.ids['grid'].add_widget(Label(text = key))
                    self.ids['grid'].add_widget(Slider(min = 0, max = 3, value = description[value['today']], value_track=True, value_track_color = color[value['today']]))
                    self.ids['grid'].add_widget(Slider(min = 0, max = 3, value = description[value['tomorrow']], value_track=True, value_track_color = color[value['today']]))
                    self.ids['grid'].add_widget(Slider(min = 0, max = 3, value = description[value['dayafter_to']], value_track=True, value_track_color = color[value['today']]))
             
    def update_states_spinner(self, *args, **kwargs):
        '''Update the spinners with all available continents and countries'''

        statesAndRegions = {}

        for element in self.dataset:
            if not element.get('region_name') in statesAndRegions.keys():
                statesAndRegions[element['region_name']] = []
            if not element.get('partregion_name') in statesAndRegions[element['region_name']]:
                statesAndRegions[element['region_name']].append(element['partregion_name'])

        self.statesAndRegions = statesAndRegions
        self.states = sorted(statesAndRegions.keys())
        if 'Baden-Württemberg' in self.states:
            self.ids['spn1'].text = 'Baden-Württemberg'
            if 'Oberrhein und unteres Neckartal' in self.regions:
                self.ids['spn2'].text = 'Oberrhein und unteres Neckartal'

class PollenTestLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(PollenTestLayout, self).__init__(**kwargs)
        self.ids['wdgt1'].download_dataset(url = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json')

class PollenWidgetApp(App):
    def build(self):
        return PollenTestLayout()

if __name__ == '__main__':
    PollenWidgetApp().run()
