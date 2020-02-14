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
import math
import re
import string

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
filelocation = _thisDir + os.sep + u'data/%s' % (expInfo['participant'])    #creates data file name
filename = os.path.join(filelocation, 'exp_data')
thisExp = data.ExperimentHandler(extraInfo = expInfo, dataFileName = filename)
logFile = logging.LogFile(filename + '.log', level = logging.EXP)               # save a log file for detail verbose info
task = int(expInfo['session'])

# Setup the Window
win = visual.Window(
    size=(1280, 800), fullscr=False, allowGUI=False,
    monitor='testMonitor', color=[1,1,1], useFBO=True)

expInfo['frameRate'] = win.getActualFrameRate()                                 # store frame rate of monitor

first_congruency = random.choice(("congruent", "incongruent"))
expInfo['first_congruency'] = first_congruency

blocks = 4
if task == 1 or task == 2:
    overall_incongruency = .5
elif task == 0:
    overall_incongruency = 0

blocks_cong_divvy = blocks * (1 + overall_incongruency)

pics_csv = (pd.read_csv('IPNP_spreadsheet.csv') >>                             # read in the csv listing the different image names and relevant info like agreement factor
            mask(X.Keep) >>
            arrange(X.Mean_RT_All))     # sorts remaining rows in csv by these columns, which indicate how difficult the images are to identify

imported_num_of_pics = len(pics_csv)
desired_main_trials = 500
trials_prac = 12
total_necessary_pics = desired_main_trials * (1 + overall_incongruency) + trials_prac

if total_necessary_pics > imported_num_of_pics:
    total_necessary_pics = imported_num_of_pics

total_necessary_main_pics = total_necessary_pics - trials_prac

used_pics_main = int(math.floor(1.0 * total_necessary_main_pics / blocks_cong_divvy) * blocks_cong_divvy)
main_trials = used_pics_main // (1 + overall_incongruency)

trials_per_block = main_trials // blocks

trials_total = trials_prac + main_trials
greater_gruency = .75
lesser_gruency = .25
greater_per_block = int(greater_gruency * trials_per_block)
lesser_per_block = trials_per_block - greater_per_block


block_trials_mjrty_prct = .75                                                               # percent of congruent or incongruent trials in overall block (in terms of whatever is greater, so this number is always >= .5)
block_trials_mnrty_prct = 1 - block_trials_mjrty_prct                                         # lesser percent in the block
trials_per_block_mjrty = trials_per_block * block_trials_mjrty_prct
trials_per_block_mnrty = trials_per_block * block_trials_mnrty_prct
new_step = fractions.gcd(block_trials_mjrty_prct, block_trials_mnrty_prct)

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))

fix_duration_input = .5
fix_duration = to_frames(fix_duration_input)
timeout_input = 3 + fix_duration_input
timeout = to_frames(timeout_input)                                              # how long to keep waiting for a voice response before moving on to next trial
timeout_min_input = 3 + fix_duration_input
timeout_min = to_frames(timeout_min_input)
resp_timeout_input = .5
resp_timeout = to_frames(resp_timeout_input)


##-----------------------------STIMULI LOADING--------------------------------##

fix = visual.TextStim(win=win, name = 'fix', color='black',text='+')            # create fixation cross

recordlocation = _thisDir + os.sep + u'data/%s/%s/%s' % (expInfo['participant'], 'audio', 'full_recording') 
os.makedirs(recordlocation)
mic_1 = microphone.AdvAudioCapture(name = 'mic_1', filename = os.path.join(recordlocation, 'full_recording') + '.wav', stereo=False, chnl=0)

@make_symbolic                                                                  # this line is required to apply the function to column name like dplyr, which as a reminder also uses unquoted symbols for column names
def to_ceil(x):                                                                 # round to ceiling; this is outside the dfply chain because for whatever reason dfply doesn't like numpy
    return np.ceil(x)

@make_symbolic                                                                  # ditto same line in the `to_ceil` function
def to_floor(x):                                                                # round to floor; like above, this is outside the dfply chain because for whatever reason dfply doesn't like numpy
    return np.floor(x)

pics_csv_prelim_dply = (pics_csv >>
    head(used_pics_main + trials_prac) >>            # keep only the top remaining rows in the csv so that the number of rows equals the number of trials + the number of incongruent trials
    sample(frac = 1))                                                        # randomize the remaining rows

faux_string_length = 6
skip_letters = '[aeiouyl]'
remaining_letters = re.sub(skip_letters, "", string.ascii_lowercase)


pics_csv_main = (pics_csv_prelim_dply >>
    head(used_pics_main) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, int(main_trials * (1 - overall_incongruency)))) >> # assign potential incongruent word, which is just the Dominant Response main_trials * (1 - overall_incongruency) rows below
    mutate(row_num_setup = 1) >>                                                # creates new column (1 is just a filler number)...
    mutate(row_num = row_number(X.row_num_setup)) >>                            # ...which then gets converted into row_number rankings (apparently can't just create this new column of row numbers in just one line)
    mutate(congruency = if_else(X.row_num <= main_trials * (1 - overall_incongruency), "congruent", "incongruent")) >> # if the row number is <= main_trials * overall_incongruency, then it's a congruent trial; otherwise it's incongruent
    head(main_trials) >>                                                    # now that we've extracted the bottom rows just for `Lead_Dominant_Response`, we can dispose of them
    mutate(label = if_else(X.congruency == "congruent", X.Dominant_Response, X.Lead_Dominant_Response)) >> # sets up the word that will be overlaid on each trial
    group_by(X.congruency) >>
    mutate(row_num_by_cngrcy = dense_rank(X.row_num)) >>                        # create new row numbers separately for congruent and incongruent trials
    mutate(row_num_by_cngrcy_grouped = to_ceil(X.row_num_by_cngrcy / lesser_per_block)) >> # group congruency's row numbers by how many appearances it would make in a minority block (e.g. every .25 * size of block); should yield resulting rows such as 1, 2, 3, etc...
    # mutate(sumin = to_floor(X.row_num_by_cngrcy_grouped * new_step)) >>
    mutate(new_row_n = if_else(X.congruency == first_congruency,                     # this ifelse statement is to take the grouped rows numbers from congruent and incongruent conditions and spread them out so there is only one row value between each of the two groups, as opposed to each group sharing each number once; gets accomplished by adding to the grouped row number...
                        X.row_num_by_cngrcy + trials_per_block * (to_floor(X.row_num_by_cngrcy_grouped * new_step)), #...specifically, add to the grouped row number with a multiple of `block_size` (e.g. row number + 0*80, + 1*80, + 2*80); note, the max size of `to_floor`'s output is main_trials * overall_incongruency larger than its current row number;
                        X.row_num_by_cngrcy + greater_per_block + trials_per_block * (to_floor((X.row_num_by_cngrcy_grouped - 1) * new_step)))) >>
    ungroup() >>
    arrange(X.new_row_n) >>
    mutate(block = to_ceil(X.new_row_n / trials_per_block)) >>
    group_by(X.block) >>
    sample(frac = 1)
    )

pics_csv_dplyed = (pics_csv_prelim_dply >>
    tail(trials_prac) >>
    sample(frac = 1) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, int(trials_prac * overall_incongruency))) >>
    mutate(row_num_setup = 1) >>
    mutate(row_num = row_number(X.row_num_setup)) >>
    mutate(congruency = if_else(X.row_num <= trials_prac * overall_incongruency, "congruent", "incongruent")) >>
    mutate(label = if_else(X.congruency == "congruent", X.Dominant_Response, X.Lead_Dominant_Response)) >>
    head(trials_prac) >>
    sample(frac = 1) >>
    bind_rows(pics_csv_main, join = 'inner')
)


if task == 0:
    tama = []
    for i in range(len(pics_csv_dplyed)):
        tama.append("".join(random.choices(remaining_letters, k=faux_string_length)))

    pics_csv_dplyed['label'] = tama

pics_dir = "IPNP_Pictures_new"
adict = {}
for i, a, b in zip(pics_csv_dplyed.Dominant_Response, pics_csv_dplyed.Pic_Num, pics_csv_dplyed.label):
    adict[b.capitalize()] = (visual.ImageStim(win, image = os.path.join(pics_dir, a + i + ".png")),
                            visual.TextBox(window = win, text = b.upper(), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(b), 1]),
                            b, i)

def runTrial():
    frame_count = resp_frame_count = 0
    fix.setAutoDraw(True)                                                       # start drawing fixation at the outset of the trial since it's on the screen at the beginning of all trials
    while resp_frame_count < resp_timeout or frame_count < timeout_min:
        if event.getKeys(keyList = ["escape"]):                                 # quit out of task if escape gets pressed
            mic_1.stop()
            core.quit()
#        if frame_count < fix_duration:
#            while 
        if frame_count == fix_duration:                                         # after certain between-trial delay has elapsed...
            fix.setAutoDraw(False)                                              # ...remove fixation cross and start recording voice
            vpvkOff = vk.OffsetVoiceKey()                                       # tracks voice offset
            vpvkOn = vk.OnsetVoiceKey(sec = timeout_input)                      # tracks voice onset
            [i.start() for i in (vpvkOff, vpvkOn)]
            start_recording = globalClock.getTime()                             # timer used as reference for voice onset and offset
        elif frame_count > fix_duration:                                        # after we've started recording...
            [trial_vals[i].draw() for i in range(2)]                            # keep re-drawing the stimuli until otherwise specified
            if hasattr(vpvkOff, 'event_offset') and vpvkOff.event_offset > 0:   # if voice offset has occured...
                resp_frame_count += 1                                           # ...start timing how long it's been since speaking has ended; this is so we don't end trial at the exact moment talking ends and allows for someone to keep talking for a little bit beyond a potentially-early recording stoppage
            elif frame_count == timeout and vpvkOn.event_onset == 0:            # if we've reached the max trial time and speaking still hasn't been picked up...
                vpvkOff.event_offset = "NA"                                     # ...set event offset value to NA and...
                break                                                           # ...end trial
        frame_count += 1
        win.flip()
    vpvkOff.stop()
    vpvkOn.stop()

    for i in (('Trial', trial_num - trials_prac),                               # means that the first experimental trials ends up with a value of 0
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

if task == 0:
    sensical = "nonsense"
elif task == 1:
    sensical  = ""

inst1 = create_inst("Welcome to the study! It's a pretty straight-forward design. You'll repeatedly see images that are overlaid with a word, and every time your job is to say aloud the identity of the picture (regardless of the " + sensical + "word overlaid on top).\n\nPress space to continue.")

inst2 = create_inst("One important part of the study is that you avoid using filler words like 'um'. This will significantly help the experimenter when he analyzes your data." + continue_goback("continue"))

inst3 = create_inst("The task moves pretty fast, so you'll start off with " + str(trials_prac) + " trials to get the hang of it, before advancing to the main portion of the experiment. Please do let the experiment know either now or at any time if you have any questions."+ continue_goback("begin"))

welcmmain = create_inst("Welcome to the main portion of the experiment! It'll work just like the practice trials, only there will be many more trials. The trials will be split among " + str(blocks - 1) + " breaks, and the whole study should total no more than 25 minutes (probably less).\n\nPress space to continue.")

main_prev = create_inst("Again, please do avoid using filler words if you can. Let the experiment know if you have any questions, or otherwise, press the spacebar to begin!")

def break_message(trial_count):
    return create_inst("You've reached break " + str(int((trial_count - trials_prac) / (main_trials / blocks))) + " of " + str(blocks - 1) + ". This break is self-timed, so whenever you're ready press spacebar to continue the study.")

thanks = create_inst("Thank you so much for your participation! Let the experimenter know that you're finished, and he'll set up the 1-minute, post-study demographic survey on this computer.")

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
    if trial_num == trials_prac:                                                # when practice trials are over...
        instr_list([welcmmain, main_prev])                                      # ...run the instructions for the main task
    elif (trial_num - trials_prac) % (main_trials / blocks) == 0 and trial_num < trials_total:
        instr_list([break_message(trial_num)])
    runTrial()
    thisExp.addData('block', int((trial_num - trials_prac) / (main_trials / blocks)))
mic_1.stop()
instr_list([thanks])


thisExp.saveAsWideText(filename + '.csv')
thisExp.saveAsPickle(filename) # https://psychopy.org/builder/settings.html#data-settings
thisExp.abort()  # ensure everything is closed down or data files will save again on exit
win.close()
core.quit()
