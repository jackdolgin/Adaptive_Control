# -*- coding: utf-8 -*-
# PsychoPy is required for this experiment
# Install dplython using "pip install dfply"; i.e. on my Mac I typed into termainal: "pip install dfply"; if you're running script from the PscyhoPy app you'll also need to (at least on a Mac) copy the dfply folder into PsychoPy3 -> Contents -> Resources -> lib -> python3.6
from psychopy import locale_setup, prefs, gui, visual, core, data, event, logging, clock, prefs
import numpy as np
import pandas as pd
from dfply import *
import glob
import os
#

# Setup the Window
win = visual.Window(
    size=(1280, 800), fullscr=True, allowGUI=False,
    monitor='testMonitor', color=[1,1,1], useFBO=True)

pics_cap = 150

pics_info = pd.read_csv('IPNP_spreadsheet.csv')

allpics = os.listdir("IPNP_Pictures")


def my_test(series_element):
    return any(s.startswith(series_element) for s in allpics)

pics_info_dplyed = (pics_info >>
    mask(X.Pic_Num.apply(my_test)) >>
    arrange(X.Agreement_Factor, X.Alternative_Names, X.Mean_RT_Dominant) >>
    head(pics_cap))

d = dict([(i.capitalize(), visual.ImageStim(win, size=[0.5,0.5], image = os.path.join("IPNP_Pictures", a + i + ".png"))) for i, a in zip(pics_info_dplyed.Dominant_Response, pics_info_dplyed.Pic_Num)])

print (d)

win.close()
core.quit()
