#!/usr/bin/python
# coding: utf8

from random import random

from bokeh.layouts import column
from bokeh.models.widgets import RadioGroup
from bokeh.plotting import figure, curdoc
from bokeh.models.tools import TapTool, CrosshairTool, SaveTool, ResetTool

from reflowc.models import TempProfile, INTERPOLATIONS, PID
from reflowc.simulation import OvenSimulator


my_profile = TempProfile()
my_profile.insertPoint(0, 30)
my_profile.insertPoint(30, 50)
my_profile.insertPoint(60, 70)
my_profile.insertPoint(90, 120)


# create a plot and style its properties
TOOLS = [CrosshairTool(), TapTool(), SaveTool(), ResetTool()]
p = figure(plot_height=600, plot_width=800, title="Reflow Profile",
           tools=TOOLS, x_range=(0, 10*60), y_range=(0, 300))
profile = p.line(my_profile.timestamps, my_profile.values, legend="profile")
points = p.circle(my_profile.point_timestamps, my_profile.point_values, legend="points")
trace = p.line([], [], legend="trace", color="red")

td = trace.data_source

# Simulation
o = OvenSimulator()
pid = PID(5.0, 2.5, 2.0)
o.start()

def update_plot():
    timer = o.timer
    target = my_profile.getTarget(timer)
    temp = o.getTemp()
    i = pid.update(target, temp)
    if i > 10.0:
        o.setHeater(True, i)
        o.setFan(False)
    elif i <= -30.0:
        o.setFan(True, -i)
        o.setHeater(False)
    else:
        o.setFan(False)
        o.setHeater(False)
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

# put the button and plot in a layout and add to the document
curdoc().add_root(column(interpolation, p))
curdoc().add_periodic_callback(update_plot, 500)