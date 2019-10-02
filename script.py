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

#pics_cap = 150
pics_cap = 3
framelength = win.monitorFramePeriod
timeout = int(round(2.5/framelength))

pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")


def filter_pics(series_element):
    return any(s.startswith(series_element) for s in allpics)

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(pics_cap))

adict = dict([(i.capitalize(), (visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png")),
                                visual.TextStim(win, text = i.capitalize(), color=(-1,-1,-1),fontFiles=[os.path.join('fonts', 'Lato-Reg.ttf')])))  for i, a in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num)])
#                                visual.TextBox(window = win, text = i.capitalize(), color=(-1,-1,-1))))  for i, a in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num)])


def stim_onset(logical, sub_key):
    [adict[sub_key][i].setAutoDraw(logical) for i in range(len(adict[sub_key]))]
    
def runTrial(a_key):
    frame_count = 0
    stim_onset(True, a_key)
    filename = os.path.join("data", a_key + ".wav")

    vpvkOn = vk.OnsetVoiceKey()
    vpvkOff = vk.OffsetVoiceKey(
        sec=2, 
        file_out = filename)
    vpvkOff.start()
    vpvkOn.start()
    while frame_count < timeout:
        if event.getKeys(keyList = ["escape"]):
            core.quit()
        frame_count += 1
        win.flip()
        if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:
            break
    stim_onset(False, a_key)
    vpvkOff.stop()
    vpvkOn.stop()
    vpvk2 = vk.OffsetVoiceKey(file_in=filename)
    vpvk2.start()  # non-blocking
    frame_count = 0
    while frame_count < 100:
        if event.getKeys(keyList = ["escape"]):
            core.quit()
        frame_count += 1
        win.flip()
    print (vpvkOn.event_onset)

for key in adict:
    runTrial(key)

win.close()
core.quit()
