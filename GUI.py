__author__ = 'Alex'
#-*-coding:utf8;-*-
#qpy:2
#qpy:kivy

import kivy
#kivy.require('?.?.?')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.garden.graph import Graph, MeshLinePlot, SmoothLinePlot
from kivy.clock import Clock
import os
import datetime
import numpy as np
import pandas as pd

#global variables
# active_profile = pd.DataFrame({'time': [0], 'temperature': [0]})
# active_profile_name = ''

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(ProfileScreen, self).__init__(**kwargs)
        ### import profiles
        #if the folder for profiles doesn't exist then make one
        # global active_profile, active_profile_name
        self.load_profile_names()

        ### make widgets
        profile_gridlayout = GridLayout(cols=1, spacing=1, size_hint_y=None, id='profile_gridlayout')# BoxLayout(orientation='vertical', id='profile_gridlayout')
        profile_gridlayout.bind(minimum_height=profile_gridlayout.setter('height'))

        self.new_profile_button = Button(text='New Profile', size_hint_y=None, height=100)
        self.new_profile_button.bind(on_release=self.new_profile_popup)
        profile_gridlayout.add_widget(self.new_profile_button)

        self.select_profile_button = Button(text='Select Profile', size_hint_y=None, height=100)
        self.update_profile_dropdown()
        profile_gridlayout.add_widget(self.select_profile_button)

        box = BoxLayout(id='box', size_hint_y=None, height=300)
        profile_graph = Graph(xlabel='Time (days)', ylabel='Temperature', x_ticks_minor=1,
                                x_ticks_major=7, y_ticks_major=10,
                                y_grid_label=True, x_grid_label=True, padding=5,
                                x_grid=True, y_grid=True, xmin=0, xmax=14, ymin=0, ymax=30,
                                id='profile_graph', _with_stencilbuffer=False)
        box.add_widget(profile_graph)
        profile_gridlayout.add_widget(box)

        # initiate steps table
        steps_gridlayout = GridLayout(cols=4, id='steps_gridlayout', size_hint_y=None, height=30)
        steps_gridlayout.add_widget(Label(text='Step', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='Time (days)', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='Temp', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='', size_hint_y=None, height=30))
        profile_gridlayout.add_widget(steps_gridlayout)
        # self.update_steps() # this initiates the steps section

        # initiate plot
        # self.update_plot(start_up=True)

        self.save_button = Button(text='SAVE', size_hint_y=None, height=100)
        self.save_button.bind(on_release=self.save)
        profile_gridlayout.add_widget(self.save_button)

        self.brew_button = Button(text='Brew', size_hint_y=None, height=100)
        self.brew_button.bind(on_release=self.to_monitor_screen)
        profile_gridlayout.add_widget(self.brew_button)

        self.profile_scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height), id='profile_scrollview')
        self.profile_scrollview.add_widget(profile_gridlayout)
        self.add_widget(self.profile_scrollview)
        
    def load_profile_names(self):
        if not os.path.exists('./profiles'):
            os.mkdir('./profiles')
        # if there are available profiles then read them
        self.profile_file_names = []
        for (dirpath, dirnames, filenames) in os.walk('./profiles'):
            self.profile_file_names.extend(filenames)
        # print self.profile_file_names

    def new_profile_popup(self, event):
        self.new_profile_boxlayout = BoxLayout(orientation='vertical')
        self.new_profile_textinput = TextInput(text='Enter Profile Name')
        self.save_new_profile_button = Button(text='SAVE')
        self.save_new_profile_button.bind(on_release=self.add_profile)
        self.new_profile_boxlayout.add_widget(self.new_profile_textinput)
        self.new_profile_boxlayout.add_widget(self.save_new_profile_button)
        self.new_profile_popup = Popup(title='New Profile', content=self.new_profile_boxlayout, size_hint=(.8, .8))
        self.new_profile_popup.open()

    def add_profile(self, event):
        if self.new_profile_textinput.text+'.xlsx' in self.profile_file_names:
            self.popup = Popup(title='Error', content=Label(text='Profile name already exists\n\nPlease use a unique name'), size_hint=(0.5,0.5))
            self.popup.open()
        else:
            self.new_profile_df = pd.DataFrame(columns=('time', 'temperature'))
            self.writer = pd.ExcelWriter('./profiles/' + self.new_profile_textinput.text + '.xlsx')
            self.new_profile_df.to_excel(self.writer, self.new_profile_textinput.text, columns=['time', 'temperature'])
            self.writer.save()
            self.new_profile_popup.dismiss()
            self.update_profile_dropdown()

    def load_profile(self, button_instance):
        self.current_profile_name = button_instance.text
        self.select_profile_button.text = str(self.current_profile_name)
        self.profile_dropdown.dismiss()
        self.current_profile_df = pd.read_excel('./profiles/' + self.current_profile_name + '.xlsx')
        # print self.current_profile_df

        self.update_steps()

        # self.profile_boxlayout.remove_widget(plot)
        # self.profile_boxlayout.remove_widget(self.save_button)
        # self.profile_boxlayout.add_widget(Button(text='plot of profile goes here'))
        # self.profile_boxlayout.add_widget(self.save_button)

    def update_profile_dropdown(self):
        self.load_profile_names()
        self.profile_dropdown = DropDown(do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height), bar_width=20) #do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height), bar_width=20)
        for name in self.profile_file_names:
            self.button = Button(text=name[:-5], size_hint=(1, None), height=44)
            self.button.bind(on_release=self.load_profile)
            self.profile_dropdown.add_widget(self.button)
        self.select_profile_button.bind(on_release=self.profile_dropdown.open)

    def add_step(self, event):
        new_step = pd.DataFrame({'time': [float(self.add_time_textinput.text)], 'temperature':[float(self.add_temp_textinput.text)]})
        self.current_profile_df = self.current_profile_df.append(new_step, ignore_index=True)
        # self.save()
        self.update_steps()

    def remove_step(self, event):
        step_number = int(event.id)
        self.current_profile_df = self.current_profile_df.drop(step_number)
        self.current_profile_df.reset_index(inplace=True, drop=True)
        self.update_steps()

    def change_time(self, event):
        step_number = int(event.id)
        self.current_profile_df.set_value(step_number, 'time', float(event.text))
        self.update_steps()

    def change_temp(self, event):
        step_number = int(event.id)
        self.current_profile_df.set_value(step_number, 'temperature', float(event.text))
        self.update_steps()

    def update_plot(self, event=False):
        profile_scrollview = self.get_widget(self, 'profile_scrollview')
        profile_gridlayout = self.get_widget(profile_scrollview, 'profile_gridlayout')
        box = self.get_widget(profile_gridlayout, 'box')
        profile_graph = self.get_widget(box, 'profile_graph')

        profile_plot = SmoothLinePlot(color=[1,0,0,1])
        profile_plot.points = [(float(x[1][0]), float(x[1][1])) for x in self.current_profile_df.iterrows()] #(float(x[1][0]), float(x[1][1])) for x in self.current_profile_df.iterrows()
        # print profile_plot.points
        for plot in profile_graph.plots:
            profile_graph.remove_plot(plot)
        profile_graph.add_plot(profile_plot)

    def save(self, event=False):
        self.writer = pd.ExcelWriter('./profiles/' + self.current_profile_name + '.xlsx')
        self.current_profile_df.to_excel(self.writer, self.current_profile_name, columns=['time', 'temperature'])
        self.writer.save()
        self.update_plot()
        # active_profile = self.current_profile_df
        # active_profile_name = self.current_profile_name

    def get_widget(self, root, id):
        for child in root.children:
            if child.id == id:
                return child

    def update_steps(self, event=None, start_up=False):
        print self.current_profile_df
        self.current_profile_df.sort_values('time', inplace=True, axis='index')
        self.current_profile_df.reset_index(inplace=True, drop=True)
        print self.current_profile_df

        profile_scrollview = self.get_widget(self, 'profile_scrollview')
        profile_gridlayout = self.get_widget(profile_scrollview, 'profile_gridlayout')
        steps_gridlayout = self.get_widget(profile_gridlayout, 'steps_gridlayout')

        steps_gridlayout.clear_widgets()
        steps_gridlayout.add_widget(Label(text='Step', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='Time (days)', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='Temp', size_hint_y=None, height=30))
        steps_gridlayout.add_widget(Label(text='', size_hint_y=None, height=30))

        self.step_counter = 0
        if not start_up:
            for step in self.current_profile_df.iterrows():
                # print step[1].ix['time']
                steps_gridlayout.add_widget(Label(text=str(self.step_counter), size_hint_y=None, height=30))
                time_textinput = TextInput(text=str(step[1].ix['time']), id=str(self.step_counter), multiline=False, size_hint_y=None, height=30)
                time_textinput.bind(on_text_validate=self.change_time)
                steps_gridlayout.add_widget(time_textinput)

                temp_textinput = TextInput(text=str(step[1].ix['temperature']), id=str(self.step_counter), multiline=False, size_hint_y=None, height=30)
                temp_textinput.bind(on_text_validate=self.change_temp)
                steps_gridlayout.add_widget(temp_textinput)

                remove_button = Button(text='Remove', id=str(self.step_counter), size_hint_y=None, height=30)
                remove_button.bind(on_release=self.remove_step)
                steps_gridlayout.add_widget(remove_button)
                self.step_counter += 1
        steps_gridlayout.add_widget(Label(text=str(self.step_counter), size_hint_y=None, height=30))
        self.add_time_textinput = TextInput(text='', size_hint_y=None, height=30)
        steps_gridlayout.add_widget(self.add_time_textinput)
        self.add_temp_textinput = TextInput(text='', size_hint_y=None, height=30)
        steps_gridlayout.add_widget(self.add_temp_textinput)
        self.add_step_button = Button(text='Add', size_hint_y=None, height=30)
        self.add_step_button.bind(on_release=self.add_step)
        steps_gridlayout.add_widget(self.add_step_button)
        steps_gridlayout.height = (self.step_counter + 2) * 30

        self.update_plot()

    def to_monitor_screen(self, event):
        # active_profile = self.current_profile_df
        # active_profile_name = self.current_profile_name
        self.manager.start_brew(self.current_profile_df, self.current_profile_name)
        # self.manager.current = 'MonitorScreen'




class MonitorScreen(Screen):
    def __init__(self, **kwargs):
        super(MonitorScreen, self).__init__(**kwargs)
        # global active_profile, active_profile_name
        self.update_interval = 1 #interval between update in seconds
        # d = {'time': [0,5,5.1,10.1], 'temperature': [18,19,21,20]}
        # active_profile = pd.DataFrame(d)

    def start_brew(self, unfilled_profile, profile_name):
        self.unfilled_profile = unfilled_profile
        self.profile_name = profile_name
        self.profile = self.fill_profile(unfilled_profile)
        print self.profile
        self.paused = False
        self.start_time = datetime.datetime.now()
        self.brew_df = pd.DataFrame(columns=['time', 'temperature 1', 'temperature 2', 'state', 'target temperature'])

        monitor_gridlayout = GridLayout(id='monitor_gridlayout', cols=1, spacing=1, size_hint_y=None)
        monitor_gridlayout.bind(minimum_height=monitor_gridlayout.setter('height'))

        monitor_gridlayout.add_widget(Label(text='Temp 1: ', size_hint_y=None, height=30, id='temp_1_label'))
        monitor_gridlayout.add_widget(Label(text='Temp 2: ', size_hint_y=None, height=30, id='temp_2_label'))
        monitor_gridlayout.add_widget(Label(text='Target temp: ', size_hint_y=None, height=30, id='target_temp_label'))
        monitor_gridlayout.add_widget(Label(text='Arduino State: ', size_hint_y=None, height=30, id='arduino_state'))

        box = BoxLayout(id='box', size_hint_y=None, height=300)
        monitor_graph = Graph(xlabel='Time (days)', ylabel='Temperature', x_ticks_minor=1,
                                x_ticks_major=7, y_ticks_major=10,
                                y_grid_label=True, x_grid_label=True, padding=5,
                                x_grid=True, y_grid=True, xmin=0, xmax=int(unfilled_profile.iloc[-1]['time']+1), ymin=0, ymax=30,
                                id='monitor_graph', _with_stencilbuffer=False)
        box.add_widget(monitor_graph)
        monitor_gridlayout.add_widget(box)

        pause_button = Button(text='pause', size_hint_y=None, height=30, id='pause_button')
        pause_button.bind(on_release=self.pause)
        monitor_gridlayout.add_widget(Button(text='Pause', size_hint_y=None, height=30))

        monitor_scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height), id='monitor_scrollview')
        monitor_scrollview.add_widget(monitor_gridlayout)
        self.add_widget(monitor_scrollview)

        Clock.schedule_interval(self.update_brew, self.update_interval)


    def update_brew(self, event):
        # print self.start_time
        target_temp = self.get_target_temp()
        monitor_scrollview = self.get_widget(self, 'monitor_scrollview')
        monitor_gridlayout = self.get_widget(monitor_scrollview, 'monitor_gridlayout')

        latest_data = self.arduino(target_temp)
        # print latest_data
        latest_data['target temperature'] = pd.Series(target_temp, index=latest_data.index)
        self.brew_df = pd.concat([self.brew_df, latest_data])
        self.save_data()

        target_temp_label = self.get_widget(monitor_gridlayout, 'target_temp_label')
        target_temp_label.text = 'Target Temp: ' + str(target_temp)
        temp_1_label = self.get_widget(monitor_gridlayout, 'temp_1_label')
        temp_1_label.text = 'Temp 1: ' + str(latest_data['temperature 1'][0])
        temp_2_label = self.get_widget(monitor_gridlayout, 'temp_2_label')
        temp_2_label.text = 'Temp 2: ' + str(latest_data['temperature 2'][0])
        arduino_state_label = self.get_widget(monitor_gridlayout, 'arduino_state')
        arduino_state_label.text = 'Arduino State: ' + str(latest_data['state'][0])

        self.update_plot()

        # current temp
        #target temp
        # arduino state
        #realtime plot

    def get_target_temp(self):
        time_elapsed = datetime.datetime.now()-self.start_time
        print 't', time_elapsed
        for row in self.profile.iterrows():
            if (row[1]['time']*24*60) - time_elapsed.total_seconds() > 0:
                return row[1]['temperature']
        # self.exit()

    def pause(self, event):
        self.paused = not self.paused
        event.text == 'Resume' if event.text == 'Pause' else 'Pause'

    def get_widget(self, root, id):
        for child in root.children:
            if child.id == id:
                return child

    def arduino(self, target_temp):
        df = {'time': ['13/08/2016'], 'temperature 1': [15.2], 'temperature 2': [16.0], 'state': ['heat']}
        df = pd.DataFrame(df)
        return df

    def save_data(self):
        self.writer = pd.ExcelWriter('./brew data/' + self.profile_name + '_' + str(datetime.date.today()) + '.xlsx')
        self.brew_df.to_excel(self.writer, self.profile_name + '_' + str(datetime.date.today()))
        self.writer.save()

    def update_plot(self, event=False):
        monitor_scrollview = self.get_widget(self, 'monitor_scrollview')
        monitor_gridlayout = self.get_widget(monitor_scrollview, 'monitor_gridlayout')
        box = self.get_widget(monitor_gridlayout, 'box')
        monitor_graph = self.get_widget(box, 'monitor_graph')

        profile_plot = SmoothLinePlot(color=[1,0,0,1])
        profile_plot.points = [(float(x[1]['time']), float(x[1]['temperature'])) for x in self.unfilled_profile.iterrows()] #(float(x[1][0]), float(x[1][1])) for x in self.current_profile_df.iterrows()
        # brew_plot = SmoothLinePlot(color=[0,1,0,1])
        # brew_plot.points = [(float(x[1][0]), float(x[1][1])) for x in self.brew_df.iterrows()]
        for plot in monitor_graph.plots:
            monitor_graph.remove_plot(plot)
        monitor_graph.add_plot(profile_plot)

    def exit(self):
        self.save_data()
        # set arduino to hold and disconnect bluetooth
        self.manager.current = 'ProfileScreen'

    def fill_profile(self, profile):
        df = pd.DataFrame(columns=['time', 'temperature'])
        for idx in range(len(profile)-1):
            time_points = pd.Series(np.arange(profile.ix[idx]['time'], profile.ix[idx+1]['time'], 1.0/24)) #hourly
            temp_points = pd.Series(np.linspace(profile.ix[idx]['temperature'], profile.ix[idx+1]['temperature'], len(time_points)))
            df = df.append(pd.DataFrame({'time': time_points,
                                         'temperature': temp_points}),
                           ignore_index=True)
        return df


class IncuBeerTorScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(IncuBeerTorScreenManager, self).__init__(**kwargs)
        self.profile_screen = ProfileScreen(name='ProfileScreen', id='profile_screen')
        self.add_widget(self.profile_screen)
        self.monitor_screen = MonitorScreen(name='MonitorScreen', id='monitor_screen')
        self.add_widget(self.monitor_screen)
        self.current = 'ProfileScreen'

    def start_brew(self, profile, profile_name):
        self.monitor_screen.start_brew(profile, profile_name)
        self.current = 'MonitorScreen'

class IncuBeerTorApp(App):
    def build(self):
        self.incubeertor_screen_manager = IncuBeerTorScreenManager(id='incubeertor_screen_manager')
        # self.screen_manager = ScreenManager(id='screen_manager')
        # self.screen_manager.add_widget(ProfileScreen(name='ProfileScreen', id='profile_screen'))
        # self.screen_manager.add_widget(MonitorScreen(name='MonitorScreen', id='monitor_screen'))
        # self.screen_manager.current = 'ProfileScreen'
        return self.incubeertor_screen_manager
        # return Label(text='Hello world')



if __name__ == '__main__':
    IncuBeerTorApp().run()