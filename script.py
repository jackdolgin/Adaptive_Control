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

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))

timeout_input = 3
timeout = to_frames(timeout_input)
resp_timeout_input = 1
resp_timeout = to_frames(resp_timeout_input)
fix_duration = to_frames(.5)

pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")

trialClock = core.Clock()


def filter_pics(series_element):
    return any(s.startswith(series_element) for s in allpics)

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(pics_cap))

fix = visual.TextStim(win=win, name = 'fix', color='black',text='+')

adict = dict([(i.capitalize(), (visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png")),
#                                visual.TextStim(win, text = i.upper(), color=(-1,-1,-1),fontFiles=[os.path.join('fonts', 'Lato-Reg.ttf')])))  for i, a in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num)])
                                visual.TextBox(window = win, text = i.upper(), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(i), 1])))  for i, a in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num)])


def stim_onset(logical, sub_key):
    [adict[sub_key][i].setAutoDraw(logical) for i in range(len(adict[sub_key]))]
    
def runTrial(a_key):
    fix_count = frame_count = resp_frame_count = 0
    while fix_count < fix_duration:
        fix.draw()
        fix_count += 1
        win.flip()
#    stim_onset(True, a_key)
    vpvkOff = vk.OffsetVoiceKey()
    vpvkOn = vk.OnsetVoiceKey(
        sec = timeout_input,
        file_out = os.path.join("data", a_key + ".wav"))
    [i.start() for i in (vpvkOff, vpvkOn)]
    trialClock.reset()
    while frame_count < timeout and resp_frame_count < resp_timeout:
        if event.getKeys(keyList = ["escape"]): core.quit()
        [adict[a_key][i].draw() for i in range(len(adict[a_key]))]
        if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:
            resp_frame_count += 1 
        win.flip()
#    stim_onset(False, a_key)
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
