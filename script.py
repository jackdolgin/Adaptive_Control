# -*- coding: utf-8 -*-
# PsychoPy is required for this experiment
# Install dplython using "pip install dfply"; i.e. on my Mac I typed into terminal: "pip install dfply"; if you're running script from the PscyhoPy app you'll also need to (at least on a Mac) copy the dfply folder into PsychoPy3 -> Contents -> Resources -> lib -> python3.6
#https://github.com/kieferk/dfply/issues/86#issuecomment-533351436
# or on PC add it inside the following folder: PsychoPy3\Lib\site-packages; can also just download the folder from https://github.com/kieferk/dfply;
# once you have the dfply folder, you want to take its inner folder that is also called dfply and that's the folder to copy into psychopy's python directory
from dfply import *
from psychopy import locale_setup, prefs, gui, visual, core, data, event, logging, clock, prefs, microphone
from psychopy.visual import textbox
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

framelength = win.monitorFramePeriod
def to_frames(t):                                                               # Converts time to frames accounting for the computer's refresh rate (aka framelength); input is the desired time on screen, but the ouput is the closest multiple of the refresh rate
    return int(round(t / framelength))
    

earliest_possible_timeout_input = 3
earliest_possible_timeout = to_frames(earliest_possible_timeout_input)
timeout_1_input = 3
timeout_1 = to_frames(timeout_1_input)                                              # how long to keep waiting for a voice response before moving on to next trial

talk_spillover_input = .5
talk_spillover = to_frames(talk_spillover_input)
fix_duration_input = .75
fix_duration = to_frames(fix_duration_input)
ITI_talking_penalty_input = .1
ITI_talking_penalty = to_frames(ITI_talking_penalty_input)





##-----------------------------STIMULI LOADING--------------------------------##

fix = visual.TextStim(win=win, color='black', text='+')            # create fixation cross

recordlocation = _thisDir + os.sep + u'data/%s/%s/%s' % (expInfo['participant'], 'audio', 'full_recording') 
os.makedirs(recordlocation)
mic_1 = microphone.AdvAudioCapture(name = 'mic_1', filename = os.path.join(recordlocation, 'full_recording') + '.wav', stereo=False, chnl=0)


if task < 2:
    x_distance = 0
else:
    x_distance = 9
    side_randomizer = random.choice([-1, 1])
    x_distance *= side_randomizer
    
##----------------------------- TRIAL MATRIXING-------------------------------##

trial_types = ["congruent", "incongruent"]
random.shuffle(trial_types)
first_congruency = majority_left = trial_types[0]
expInfo['first_congruency'] = first_congruency
second_congruency = majority_right = trial_types[1]



if task == 1:
    
    congruent_block_dominance = .75
    incongruent_block_dominance = .75
    
else:
    congruent_block_dominance = .5
    incongruent_block_dominance = .5

block_sequence = [first_congruency, second_congruency, first_congruency, second_congruency]

blocks = len(block_sequence)

numerator = 0

for i in block_sequence:
    if i == "congruent":
        numerator += congruent_block_dominance
    elif i == "incongruent":
        numerator += 1 - incongruent_block_dominance

congruent_overall = numerator / blocks

incongruent_overall = 1 - congruent_overall
incongruent_multiplier = 1 + incongruent_overall
congruent_overall = 1 - incongruent_overall

if task == 2:
    congruent_side_dominance = .75
    incongruent_side_dominance = .75

else:
    congruent_side_dominance = incongruent_side_dominance = .5




pic_csv = (pd.read_csv('IPNP_spreadsheet.csv') >>                             # read in the csv listing the different image names and relevant info like agreement factor
            mask(X.Keep) >>
            arrange(X.Mean_RT_All))     # sorts remaining rows in csv by these columns, which indicate how difficult the images are to identify

def total_pics_func():
    return prac_pics + main_pics

actual_pics = len(pic_csv)
prac_trials = 12
prac_pics = int(prac_trials * incongruent_multiplier)
main_trials = 500
main_pics = int(main_trials * incongruent_multiplier)
pics_needed = total_pics_func()

if pics_needed > actual_pics:
    pics_needed = actual_pics
    main_trials  = int((pics_needed - prac_pics) / incongruent_multiplier)
    pics_needed = total_pics_func()


def floor_to_multiple(x, y):
    return int(math.floor(1.0 * x / y) * y)

main_trials = floor_to_multiple(main_trials, blocks)

pic_csv = (pic_csv >>
    head(pics_needed) >>            # keep only the top remaining rows in the csv so that the number of rows equals the number of trials + the number of incongruent trials
    sample(frac = 1)                                                         # randomize the remaining rows
)

@make_symbolic                                                                  # this line is required to apply the function to column name like dplyr, which as a reminder also uses unquoted symbols for column names
def to_ceil(x):                                                                 # round to ceiling; this is outside the dfply chain because for whatever reason dfply doesn't like numpy
    return np.ceil(x)


@make_symbolic
def tomaba(series_element):
    my_min = main_trials * congruent_overall * congruent_side_dominance
    my_max = main_trials * congruent_overall + main_trials * incongruent_overall * incongruent_side_dominance
    marsh = np.logical_and(my_min <= series_element, series_element < my_max)
    return if_else(marsh, x_distance, -x_distance)

@dfpipe
def df_pipe(df, pic_total, trial_total, top_or_bottom):
  df_for_piping = (df >>
    top_or_bottom(pic_total) >>
    mutate(Lead_Dominant_Response = lead(X.Dominant_Response, int(trial_total * incongruent_overall))) >>
    mutate(row_num_setup = 1) >>                                                # creates new column (`1` is just a filler number)...
    mutate(row_num = row_number(X.row_num_setup)) >>                            # ...which then gets converted into row_number rankings (apparently can't just create this new column of row numbers in just one line)
    mutate(congruency = if_else(X.row_num <= trial_total * congruent_overall, "congruent", "incongruent")) >>
    mutate(label = if_else(X.congruency == "congruent", X.Dominant_Response, X.Lead_Dominant_Response)) >>
    mutate(x_pos = tomaba(X.row_num)) >>
    head(trial_total) >>
    sample(frac = 1)
  )
  return df_for_piping


main_trials_dplyed = (pic_csv >>
    df_pipe(main_pics, main_trials, head)
)

trials_per_block = int(len(main_trials_dplyed) / blocks)

block = -1
new_row_order = []

congruent_per_cong_block = int(trials_per_block * congruent_block_dominance)
incongruent_per_cong_block = trials_per_block - congruent_per_cong_block
incongruent_per_incong_block = int(trials_per_block * incongruent_block_dominance)
congruent_per_incong_block = trials_per_block - incongruent_per_incong_block


for a_row in range(len(main_trials_dplyed)):
    
    if len(new_row_order) % trials_per_block == 0:
        block += 1
        block_dominance = block_sequence[block]

        if block_dominance == "congruent":
            matching_per_block = congruent_per_cong_block
            non_matching_per_block = incongruent_per_cong_block
        elif block_dominance == "incongruent":
            matching_per_block = incongruent_per_incong_block
            non_matching_per_block = congruent_per_incong_block
            
        matching_count = non_matching_count = 0
    
    
    row_counter = -1
    
    while True:
        
        row_counter += 1
        
        if row_counter not in new_row_order:
            gruency = main_trials_dplyed.iloc[row_counter].congruency
            if gruency == block_dominance and matching_count < matching_per_block:
                matching_count += 1
                break                    
            elif gruency != block_dominance and non_matching_count < non_matching_per_block:
                non_matching_count += 1
                break
                
                
    new_row_order.append(row_counter)

@make_symbolic
def implement_new_order(y):
    return new_row_order.index(y - 1)

main_trials_dplyed = (main_trials_dplyed >>
    mutate(row_num = row_number(X.row_num_setup)) >>
    mutate(row_num = X.row_num.apply(implement_new_order)) >>
    arrange(X.row_num) >>
    mutate(block = to_ceil((X.row_num  + 1) / trials_per_block)) >>
    group_by(X.block) >>
    sample(frac = 1)
)

ready_for_matrix = (pic_csv >>
    df_pipe(prac_pics, prac_trials, tail) >>
    mutate(block = -1) >>
    sample(frac = 1) >>
    bind_rows(main_trials_dplyed, join = 'inner')
)


if task == 0:
    
    faux_string_length = 5
    skip_letters = '[aeilouy]'
    remaining_letters = re.sub(skip_letters, "", string.ascii_lowercase)
    
    tama = []
    for i in range(len(ready_for_matrix)):
        tama.append("".join(random.choices(remaining_letters, k=faux_string_length)))

    ready_for_matrix['label'] = tama
    
pics_dir = "IPNP_Pictures_new"
adict = {}
for i, a, b, x, bl in zip(ready_for_matrix.Dominant_Response, ready_for_matrix.Pic_Num, ready_for_matrix.label, ready_for_matrix.x_pos, ready_for_matrix.block):
    adict[b.capitalize()] = ((visual.ImageStim(win, image = os.path.join(pics_dir, a + i + ".png"), pos = (x, 0), units = 'cm'),
                            visual.TextBox(window = win, text = b.upper(), font_name = bytes("Consolas", encoding= 'utf-8'), font_color=(-1,-1,-1), background_color = [1,1,1,.8], textgrid_shape=[len(b), 1], pos = (x, 0), units = 'cm')),
                            b, i, x, bl)


def runTrial():

    def proceed_or_stop():
        if event.getKeys(keyList = ["escape"]):                                 # quit out of task if escape gets pressed
            mic_1.stop()
            core.quit()

        win.flip()
    
    timeout_2 = talk_spillover + fix_duration
    vpvkOff = vk.OffsetVoiceKey()                                       # tracks voice offset
    vpvkOn = vk.OnsetVoiceKey(sec = timeout_1 + timeout_2)                      # tracks voice onset (note- without the `sec = ` parameter, it's possible there will be an error that the baseline is too quiet
    [i.start() for i in (vpvkOff, vpvkOn)]

    start_recording = globalClock.getTime()                             # timer used as reference for voice onset and offset
    vpvkOff.event_offset = 0                                             # do i need this line?
    frames_transpired_1 = frames_transpired_2 = 0
 
 
    while vpvkOff.event_offset == 0 or frames_transpired_1 < earliest_possible_timeout:

        [i.draw() for i in trial_vals[0]]

        if frames_transpired_1 >= timeout_1 and vpvkOn.event_onset == 0:
            break
            
        frames_transpired_1 += 1
        proceed_or_stop()
        


    for i in (('Trial', trial_num - prac_trials),                               # means that the first experimental trials ends up with a value of 0
                   ('Picture_Identity', trial_vals[2]),
                   ('Picture_Label', trial_vals[1]),
                   ('Display_Side', trial_vals[3]),
                   ('Response_Time', vpvkOn.event_onset),
                   ('Response_Finish', vpvkOff.event_offset),
                   ('Stim_Onset_in_Overall_Exp', start_recording),
                   ('block', trial_vals[4])):
        
        thisExp.addData(i[0], i[1])
    
    thisExp.nextEntry()



    while frames_transpired_2 < timeout_2:
        
        if frames_transpired_2 < talk_spillover:

            [i.draw() for i in trial_vals[0]]
        elif (trial_num + 1) % trials_per_block != 0:
            fix.draw()

        if vpvkOn.power[-1] >= 50:
            timeout_2 += ITI_talking_penalty
        
        frames_transpired_2 += 1
        
        proceed_or_stop()
    
    [i.stop() for i in (vpvkOff, vpvkOn)]




##-------------------------------INSTRUCTION SCREEN---------------------------##

def create_inst(t):
    return visual.TextStim(win = win, text = t, units = 'deg', pos = (0, 0),
        height = 1, wrapWidth = 18, color = 'black')

def continue_goback(s):
    return "\n\nPress space to " + s + " or \"B\" to go back."

if task == 0:
    sensical = "nonsense characters"
elif task == 1 or task == 2:
    sensical  = "word"

inst1 = create_inst("Welcome to the study! It's a pretty straight-forward design. You'll repeatedly see images that are overlaid with a word, and every time your job is to say aloud the identity of the picture (regardless of the " + sensical + " overlaid on top).\n\nPress space to continue.")

inst2 = create_inst("One important part of the study is that you avoid using filler words like 'um'. This will significantly help the experimenter when he analyzes your data." + continue_goback("continue"))

inst3 = create_inst("The task moves pretty fast, so you'll start off with " + str(prac_trials) + " trials to get the hang of it, before advancing to the main portion of the experiment. Please do let the experiment know either now or at any time if you have any questions."+ continue_goback("begin"))

welcmmain = create_inst("Welcome to the main portion of the experiment! It'll work just like the practice trials, only there will be many more trials. The trials will be split among " + str(blocks - 1) + " breaks, and the whole study should total no more than 25 minutes (probably less).\n\nPress space to continue.")

main_prev = create_inst("Again, please do avoid using filler words if you can. Let the experiment know if you have any questions, or otherwise, press the spacebar to begin!")

def break_message(block_num):
    return create_inst("You've reached break " + str(int(block_num)) + " of " + str(blocks - 1) + ". This break is self-timed, so whenever you're ready press spacebar to continue the study.")

thanks = create_inst("Thank you so much for your participation! Let the experimenter know that you're finished, and he'll set up the 1-minute, post-study demographic survey on this computer.")

def blockdelay():
    frameN = -1
    while frameN < to_frames(1.5):
        frameN += 1
        win.flip()

def instr_list(thelist):
    advance = 0                                                                 # a variable that advances the instruction screen, as well as lets them go back to see a previous instruction screen

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

    blockdelay()

instr_list([inst1, inst2, inst3])
mic_1.record(sec=100000, block=False)                                           # sets an impossibly long time-out window so recording will last the whole experiment
globalClock = core.MonotonicClock()                                             # to track the time since experiment started
for trial_num, (trial_key, trial_vals) in enumerate(adict.items()):
    trial_num -= prac_trials
    if trial_num % trials_per_block == 0:
        if trial_num == 0:                                                # when practice trials are over...
            instr_list([welcmmain, main_prev])                                      # ...run the instructions for the main task
        elif trial_num < main_trials:
            instr_list([break_message(trial_vals[4])])
        fix.setAutoDraw(True) #ideally get rid of this line and the one two below
        blockdelay()
        fix.setAutoDraw(False)
    runTrial()

mic_1.stop()
instr_list([thanks])


thisExp.saveAsWideText(filename + '.csv')
thisExp.saveAsPickle(filename) # https://psychopy.org/builder/settings.html#data-settings
thisExp.abort()  # ensure everything is closed down or data files will save again on exit
win.close()
core.quit()
