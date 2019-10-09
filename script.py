# -*- coding: utf-8 -*-
# PsychoPy is required for this experiment
# Install dplython using "pip install dfply"; i.e. on my Mac I typed into termainal: "pip install dfply"; if you're running script from the PscyhoPy app you'll also need to (at least on a Mac) copy the dfply folder into PsychoPy3 -> Contents -> Resources -> lib -> python3.6
#https://github.com/kieferk/dfply/issues/86#issuecomment-533351436
# or on PC add it inside the following folder: PsychoPy3\Lib\site-packages; can also just download the folder from https://github.com/kieferk/dfply;
# once you have the dfply folder, you want to take its inner folder that is also called dfply and that's the folder to copy into psychopy's python directory
from psychopy import locale_setup, prefs, gui, visual, core, data, event, logging, clock, prefs
import numpy as np
import pandas as pd
from dfply import *
import random
import glob
import os
import psychopy.voicekey as vk

vk.pyo_init()

## Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

## Setup the Window
win = visual.Window(
    size=(1280, 800), fullscr=True, allowGUI=False,
    monitor='testMonitor', color=[1,1,1], useFBO=True)

pics_cap = 200
pct_split = .75
bigger_group = round(pics_cap * pct_split)
two_groups = random.sample((bigger_group, pics_cap - bigger_group), 2)

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))

fix_duration_input = .5
fix_duration = to_frames(.5)
timeout_input = 3 + fix_duration_input
timeout = to_frames(timeout_input)
resp_timeout_input = 1
resp_timeout = to_frames(resp_timeout_input)


pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")

trialClock = core.Clock()

def filter_pics(series_element):
    return any(s.startswith(series_element) for s in allpics)

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(pics_cap + bigger_group) >>
    sample(frac = 1) >>
    mutate(Lag_Dominant_Response = lag(X.Dominant_Response, bigger_group)))

fix = visual.TextStim(win=win, name = 'fix', color='black',text='+')


adict = {}
for i, a, b in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num, range(pics_cap)):
    adict[i.capitalize()] = (visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png")),
                            visual.TextBox(window = win, text = i.upper(), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(i), 1]))

def runTrial(a_key):
    frame_count = resp_frame_count = 0
    fix.setAutoDraw(True)
    while frame_count < timeout and resp_frame_count < resp_timeout:
        if event.getKeys(keyList = ["escape"]): core.quit()
        if frame_count == fix_duration:
            fix.setAutoDraw(False)
            vpvkOff = vk.OffsetVoiceKey()
            vpvkOn = vk.OnsetVoiceKey(
                sec = timeout_input,
                file_out = os.path.join("data", a_key + ".wav"))
            [i.start() for i in (vpvkOff, vpvkOn)]
            trialClock.reset()
        elif fix_duration < frame_count < timeout and resp_frame_count < resp_timeout:
            [adict[a_key][i].draw() for i in range(len(adict[a_key]))]
            if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:
                resp_frame_count += 1
        frame_count += 1
        win.flip()
    vpvkOff.stop()
    vpvkOn.stop()

#    vpvk2 = vk.OffsetVoiceKey(file_in=os.path.join("data", a_key + ".wav"))
#    vpvk2.start()  # non-blocking
#    frame_count = 0
#    while frame_count < 100:
#        if event.getKeys(keyList = ["escape"]):
#            core.quit()
#        frame_count += 1
#        win.flip()

for key in adict:
    runTrial(key)

win.close()
core.quit()
