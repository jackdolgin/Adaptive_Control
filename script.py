# -*- coding: utf-8 -*-
# PsychoPy is required for this experiment
# Install dplython using "pip install dfply"; i.e. on my Mac I typed into terminal: "pip install dfply"; if you're running script from the PscyhoPy app you'll also need to (at least on a Mac) copy the dfply folder into PsychoPy3 -> Contents -> Resources -> lib -> python3.6
#https://github.com/kieferk/dfply/issues/86#issuecomment-533351436
# or on PC add it inside the following folder: PsychoPy3\Lib\site-packages; can also just download the folder from https://github.com/kieferk/dfply;
# once you have the dfply folder, you want to take its inner folder that is also called dfply and that's the folder to copy into psychopy's python directory
from dfply import *
from psychopy import locale_setup, prefs, gui, visual, core, data, event, logging, clock, prefs, microphone
import numpy as np
import pandas as pd
import fractions
import random
import glob
import os
import psychopy.voicekey as vk

microphone.switchOn()
vk.pyo_init()


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
expInfo = {'participant':'','session':''}                                       # creates dictionary of experiment information
if gui.DlgFromDict(dictionary=expInfo).OK == False:                             # creates popup at beginning of experiment that asks for participant number
    core.quit()                                                                 # says, if you hit escape/click cancel when that popup appears, then don't run the experiment; if this if statement didn't exist, experiment would run regardly of whether you hit escape/click cancel
expInfo['date'] = data.getDateStr()                                             # add a simple timestamp
filename = _thisDir + os.sep + u'data/%s/%s' % (expInfo['participant'], 'exp_data')    #creates data file name
thisExp = data.ExperimentHandler(extraInfo = expInfo, dataFileName = filename)
logFile = logging.LogFile(filename + '.log', level = logging.EXP)               # save a log file for detail verbose info

# Setup the Window
win = visual.Window(
    size=(1280, 800), fullscr=True, allowGUI=False,
    monitor='testMonitor', color=[1,1,1], useFBO=True)

expInfo['frameRate'] = win.getActualFrameRate()                                 # store frame rate of monitor

first_congruency = random.choice(("congruent", "incongruent"))
expInfo['first_congruency'] = first_congruency
blocks = 4
prac_trials = 12
pics_cap = 320
block_trials = pics_cap / blocks
all_trials = prac_trials + pics_cap
cong_split = .5
block_split = .75
block_split_remainder = 1 - block_split
new_step = 1 / fractions.gcd(block_split, block_split_remainder)
block_majority_trials = block_trials * block_split
block_minority_trials = block_trials * block_split_remainder

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))

fix_duration_input = .5
fix_duration = to_frames(fix_duration_input)
timeout_input = 3 + fix_duration_input
timeout = to_frames(timeout_input)
timeout_min_input = 3 + fix_duration_input
timeout_min = to_frames(timeout_min_input)
resp_timeout_input = .5
resp_timeout = to_frames(resp_timeout_input)

mic_1 = microphone.AdvAudioCapture(name='mic_1', filename= filename + '.wav', stereo=False, chnl=0)

pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")

def filter_pics(series_element):
    return any(s.startswith(series_element) for s in allpics)

@make_symbolic
def to_ceil(x):
    return np.ceil(x)

@make_symbolic
def to_floor(x):
    return np.floor(x)

pics_info_dplyed0 = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(int(pics_cap * (1 + cong_split))) >>
    sample(frac = 1) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, int(pics_cap * cong_split))) >>
    mutate(row_num_setup = 1) >>
    mutate(row_num = row_number(X.row_num_setup)) >>
    mutate(congruency = if_else(X.row_num <= pics_cap * cong_split, "congruent", "incongruent")) >>
    mutate(label = if_else(X.congruency == "congruent", X.Dominant_Response, X.Lead_Dominant_Response)) >>
    head(pics_cap) >>
    group_by(X.congruency) >>
    mutate(cong_order = dense_rank(X.row_num)) >>
    mutate(cong_order_clustered = to_ceil(X.cong_order / block_minority_trials)) >>
    mutate(sumin = to_floor(X.cong_order_clustered / new_step)) >>
    mutate(new_row_n = if_else(X.congruency == "congruent",
                        X.cong_order + block_trials * (to_floor(X.cong_order_clustered / new_step)),
                        X.cong_order + block_majority_trials + block_trials * (to_floor((X.cong_order_clustered - 1) / new_step)))) >>
    ungroup() >>
    arrange(X.new_row_n) >>
    mutate(block = to_ceil(X.new_row_n / block_trials)) >>
    group_by(X.block) >>
    sample(frac = 1)
    )
    

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(filter_pics)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    tail(int(prac_trials * (1 + cong_split))) >>
    sample(frac = 1) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, int(prac_trials * cong_split))) >>
    mutate(row_num_setup = 1) >>
    mutate(row_num = row_number(X.row_num_setup)) >>
    mutate(congruency = if_else(X.row_num <= prac_trials * cong_split, "congruent", "incongruent")) >>
    mutate(label = if_else(X.congruency == "congruent", X.Dominant_Response, X.Lead_Dominant_Response)) >>
    head(prac_trials) >>
    sample(frac = 1) >>
    bind_rows(pics_info_dplyed0, join = 'inner')
)
    

fix = visual.TextStim(win=win, name = 'fix', color='black',text='+')


adict = {}
for i, a, b in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num, pics_info_dplyed.label):
    adict[b.capitalize()] = (visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png")),
                            visual.TextBox(window = win, text = b.upper(), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(b), 1]),
                            b, i)

def runTrial():
    frame_count = resp_frame_count = 0
    fix.setAutoDraw(True)
    while resp_frame_count < resp_timeout or frame_count < timeout_min:
        if event.getKeys(keyList = ["escape"]):
            mic_1.stop()
            core.quit()
        if frame_count == fix_duration:
            fix.setAutoDraw(False)
            vpvkOff = vk.OffsetVoiceKey()
            vpvkOn = vk.OnsetVoiceKey(sec = timeout_input)
            [i.start() for i in (vpvkOff, vpvkOn)]
            start_recording = globalClock.getTime()
        elif frame_count > fix_duration:
            [trial_vals[i].draw() for i in range(2)]
            if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:
                resp_frame_count += 1
            elif frame_count == timeout and vpvkOn.event_onset == 0:
                vpvkOff.event_offset = "NA"
                break
        frame_count += 1
        win.flip()
    vpvkOff.stop()
    vpvkOn.stop()

    for i in (('Trial', trial_num - prac_trials),
               ('Picture_Identity', trial_vals[3]),
               ('Picture_Label', trial_vals[2]),
               ('Response_Time', vpvkOn.event_onset),
               ('Response_Finish', vpvkOff.event_offset),
               ('Stim_Onset_in_Overall_Exp', start_recording)):

        thisExp.addData(i[0], i[1])
    thisExp.nextEntry()


##-------------------------------INSTRUCTION SCREEN---------------------------##

def create_inst(t):
    return visual.TextStim(win = win, text = t, units = 'deg', pos = (0, 0),
        height = 1, wrapWidth = 18, color = 'black', fontFiles = ['Lato-Reg.ttf'])

def continue_goback(s):
    return "\n\nPress space to " + s + " or \"B\" to go back."

inst1 = create_inst("Welcome to the study! You will be completing a voice response task, meaning quite literally you'll be verbally responding to drawings you see.\n\nPress space to continue.")

inst2 = create_inst("On every trial you will see a drawing and an overlaid word. Some of the time the drawing will match the word, the rest of the time they will conflict. Your task is to always name the drawing (as opposed to the word). That's it!" + continue_goback("continue"))

inst3 = create_inst("The task moves pretty quickly, so to get the hang of it you'll go through the following practice trials. We ask that when you name the image, you deliver your response into the microphone." + continue_goback("begin"))

welcmmain = create_inst("Welcome to the beginning of the main experiment. This experiment will last about 20 minutes. It will feature trials split among " + str(blocks - 1) + u" breaks (which will be self-timed, so you can break as long as you’d like).\n\nPress space to continue.".encode('utf-8').decode('utf-8'))

main_prev = create_inst("The forthcoming trials will work just like the practice trials: a drawing and a word will appear, and you are tasked with verbally naming the drawing." + continue_goback("begin"))

def break_message(trial_count):
    return create_inst("You've reached break " + str(int((trial_count - prac_trials) / (pics_cap / blocks))) + " of " + str(blocks - 1) + ". This break is self-timed, so whenever you're ready press spacebar to continue the study.")

thanks = create_inst("Thank you so much for your participation! Let the experimenter know that you're finished, and he'll set up the 1-minute, post-study demographic survey.")

def instr_list(thelist):
    advance = 0
    frameN = -1                                                                 # a variable that advances the instruction screen, as well as lets them go back to see a previous instruction screen

    while advance < len(thelist):
        if event.getKeys(keyList = ["space"]):
            advance += 1
        elif event.getKeys(keyList = ["b"]):
            if advance > 0:
                advance -= 1
        for i in range(len(thelist)):
            if advance == i:
                thelist[i].setAutoDraw(True)
            else:
                thelist[i].setAutoDraw(False)
        win.flip()

    while frameN < to_frames(1.5):
        frameN += 1
        win.flip()

instr_list([inst1, inst2, inst3])
mic_1.record(sec=100000, block=False)                                           # sets an impossibly long time-out window so recording will last the whole experiment
globalClock = core.MonotonicClock()                                             # to track the time since experiment started
for trial_num, (trial_key, trial_vals) in enumerate(adict.items()):
    if trial_num == prac_trials:
        instr_list([welcmmain, main_prev])
    elif (trial_num - prac_trials) % (pics_cap / blocks) == 0 and trial_num < all_trials:
        instr_list([break_message(trial_num)])
    runTrial()
mic_1.stop()    
instr_list([thanks])


thisExp.saveAsWideText(filename + '.csv')
thisExp.saveAsPickle(filename) # https://psychopy.org/builder/settings.html#data-settings
thisExp.abort()  # ensure everything is closed down or data files will save again on exit
win.close()
core.quit()
