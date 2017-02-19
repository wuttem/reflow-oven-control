#!/usr/bin/python
# coding: utf8

import time

from random import random

from bokeh.layouts import column
from bokeh.models.widgets import RadioGroup, Button
from bokeh.models import Label
from bokeh.plotting import figure, curdoc
from bokeh.models.tools import TapTool, CrosshairTool, SaveTool, ResetTool

from reflowc.models import TempProfile, INTERPOLATIONS, PID
from reflowc.simulation import OvenSimulator
from reflowc.oven import Oven


my_profile = TempProfile()
my_profile.insertPoint(0, 40)
my_profile.insertPoint(100, 50)
my_profile.insertPoint(200, 150)
my_profile.insertPoint(300, 217)
my_profile.insertPoint(320, 250)
my_profile.insertPoint(330, 245)
my_profile.insertPoint(350, 220)
my_profile.insertPoint(450, 80)
my_profile.insertPoint(500, 70)


# create a plot and style its properties
TOOLS = [CrosshairTool(), TapTool(), SaveTool(), ResetTool()]
p = figure(plot_height=600, plot_width=800, title="Reflow Profile",
           tools=TOOLS, x_range=(0, 500), y_range=(0, 300))
profile = p.line(my_profile.timestamps, my_profile.values, legend="profile")
points = p.circle(my_profile.point_timestamps, my_profile.point_values, legend="points")
trace = p.line([], [], legend="trace", color="red")

td = trace.data_source

# Simulation
o = Oven("/dev/ttyUSB0")
pid = PID(5.0, 2.5, 2.0)
o.start()

start_time = time.time()
timer = 0.0
active = False

def on_start():
    global start_time, timer, active
    active = True
    timer = 0.0
    start_time = time.time()
    td.data['x'] = []
    td.data['y'] = []
    td.trigger('data', td.data, td.data)

def update_plot():
    timer = time.time() - start_time
    target = my_profile.getTarget(timer)
    temp = o.getTemp()
    if temp is None:
        print("waiting for temp ...")
        return

    label.text = "Temperature: {} Grad".format(temp)

    if not active:
        print("waiting for start, Temp: {}".format(temp))
        return

    i = pid.update(target, temp)
    hf = 200
    heat = 200 if i > 33 else 0
    fan = 200 if i < -33 else 0
    o.setControl(hf, heat, fan)
    # if i > 10.0:
    #     o.setHeater(True, i)
    #     o.setFan(False)
    # elif i <= -30.0:
    #     o.setFan(True, -i)
    #     o.setHeater(False)
    # else:
    #     o.setFan(False)
    #     o.setHeater(False)
    i = pid.update(target, temp)
    print("%s: Target: %06.2f, Temp: %06.2f, PID: %06.2f" % (int(timer), target, temp, i))
    td.data['x'].append(timer)
    td.data['y'].append(temp)
    td.trigger('data', td.data, td.data)

def update_profile_plot():
    global my_profile, profile, points
    p1 = {"x": my_profile.timestamps,
          "y": my_profile.values}
    p2 = {"x": my_profile.point_timestamps,
          "y": my_profile.point_values}
    profile.data_source.data = p1
    points.data_source.data = p2

def on_interpolation_changed(new):
    global my_profile
    my_profile.setInterpolation(INTERPOLATIONS[int(new)])
    update_profile_plot()

def tool_events_callback(attr, old, new):
    global my_profile, profile, points
    print attr, 'callback', new
    my_profile.insertPoint(new[0]["x"], new[0]["y"])
    update_profile_plot()

p.tool_events.on_change('geometries', tool_events_callback)

# Interpolation
interpolation = RadioGroup(
    labels=INTERPOLATIONS, active=0)
interpolation.on_click(on_interpolation_changed)

# start
start_button = Button(label="Start !!!")
start_button.on_click(on_start)

# Temp
label = Label(x=20, y=230, text="waiting ...", text_font_size='20pt', text_color='#999999')
p.add_layout(label)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(interpolation, start_button, p))
curdoc().add_periodic_callback(update_plot, 1500)