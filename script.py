# -*- coding: utf-8 -*-
# PsychoPy is required for this experiment
# Install dplython using "pip install dfply"; i.e. on my Mac I typed into termainal: "pip install dfply"; if you're running script from the PscyhoPy app you'll also need to (at least on a Mac) copy the dfply folder into PsychoPy3 -> Contents -> Resources -> lib -> python3.6
#https://github.com/kieferk/dfply/issues/86#issuecomment-533351436
# or on PC add it inside the following folder: PsychoPy3\Lib\site-packages; can also just download the folder from https://github.com/kieferk/dfply;
# once you have the dfply folder, you want to take its inner folder that is also called dfply and that's the folder to copy into psychopy's python directory
from dfply import *
from psychopy import locale_setup, prefs, gui, visual, core, data, event, logging, clock, prefs
import numpy as np
import pandas as pd
import random
import glob
import os
import psychopy.voicekey as vk

vk.pyo_init()


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
expInfo = {'participant':'','session':''}
if gui.DlgFromDict(dictionary=expInfo).OK == False:
    core.quit()                                                                 # user pressed cancel during popout
expInfo['date'] = data.getDateStr()                                             # add a simple timestamp
thisExp = data.ExperimentHandler(extraInfo=expInfo, dataFileName='afile')       # an ExperimentHandler isn't essential but helps with data saving

# Setup the Window
win = visual.Window(
    size=(1280, 800), fullscr=True, allowGUI=False,
    monitor='testMonitor', color=[1,1,1], useFBO=True)

pics_cap = 200
pct_split = .75
common_trials = round(pics_cap * pct_split)
cong_trials = random.choice((common_trials, pics_cap - common_trials))

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))

fix_duration_input = .5
fix_duration = to_frames(fix_duration_input)
timeout_input = 3 + fix_duration_input
timeout = to_frames(timeout_input)
resp_timeout_input = .5
resp_timeout = to_frames(resp_timeout_input)


pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")

trialClock = core.Clock()

def filter_pics(series_element):
    return any(s.startswith(series_element) for s in allpics)

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(pics_cap + common_trials) >>
    sample(frac = 1) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, common_trials),
           row_num_setup = 1) >>
    mutate(row_num = row_number(X.row_num_setup)) >>
    mutate(label = if_else(X.row_num <= pics_cap - cong_trials, X.Dominant_Response, X.Lead_Dominant_Response)) >>
    head(pics_cap) >>
    sample(frac = 1) >>
    mutate(row_num = row_number(X.row_num_setup)))

fix = visual.TextStim(win=win, name = 'fix', color='black',text='+')


adict = {}
for i, a, b, c in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num, pics_info_dplyed.label, pics_info_dplyed.row_num):
    adict[b.capitalize()] = (visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png")),
                            visual.TextBox(window = win, text = b.upper(), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(b), 1]),
                            b, i, c)

def runTrial(a_key):
    trial_dict = adict[a_key]
    frame_count = resp_frame_count = 0
    fix.setAutoDraw(True)
    while resp_frame_count < resp_timeout:
        if event.getKeys(keyList = ["escape"]): core.quit()
        if frame_count == fix_duration:
            fix.setAutoDraw(False)
            vpvkOff = vk.OffsetVoiceKey()
            vpvkOn = vk.OnsetVoiceKey(
                sec = timeout_input,
                file_out = os.path.join("data", a_key + ".wav"))
            [i.start() for i in (vpvkOff, vpvkOn)]
            trialClock.reset()
        elif frame_count > fix_duration:
            [trial_dict[i].draw() for i in range(2)]
            if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:
                resp_frame_count += 1
            elif frame_count == timeout and vpvkOn.event_onset == 0:
                break
        frame_count += 1
        win.flip()
    vpvkOff.stop()
    vpvkOn.stop()
    
    for i in (('Trial', trial_dict[4]),
               ('Picture_Identity', trial_dict[3]),
               ('Picture_Label', trial_dict[2]),
               ('Response_Time', vpvkOn.event_onset),
               ('Response_Finish', vpvkOff.event_offset)):
        
        thisExp.addData(i[0], i[1])
    thisExp.nextEntry()
    
for key in adict:
    runTrial(key)

thisExp.abort()  # ensure everything is closed down or data files will save again on exit
win.close()
core.quit()
