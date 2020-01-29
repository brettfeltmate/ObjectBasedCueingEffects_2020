### Klibs Parameter overrides ###

from klibs import P

#########################################
# Runtime Settings
#########################################
collect_demographics = True
manual_demographics_collection = False
manual_trial_generation = False
run_practice_blocks = True
multi_user = False
view_distance = 57 # in centimeters, 57cm = 1 deg of visual angle per cm of screen

#########################################
# Available Hardware
#########################################
eye_tracker_available = True
eye_tracking = True

#########################################
# Environment Aesthetic Defaults
#########################################
default_fill_color = (0, 0, 0, 255)
default_color = (255, 255, 255, 255)
default_font_size = 28
default_font_unit = 'px'
default_font_name = 'Frutiger'

#########################################
# EyeLink Settings
#########################################
manual_eyelink_setup = False
manual_eyelink_recording = False

saccadic_velocity_threshold = 20
saccadic_acceleration_threshold = 5000
saccadic_motion_threshold = 0.15

#########################################
# PROJECT-SPECIFIC VARS
#########################################
saccade_response_cond = P.condition == 'saccade'  # Defaults to 'keypress' unless specified
keypress_response_cond = (saccade_response_cond == False)


#########################################
# Experiment Structure
#########################################
multi_session_project = False
if saccade_response_cond:
    trials_per_block = 32
    blocks_per_experiment = 12
else:
    trials_per_block = 40
    blocks_per_experiment = 10
trials_per_participant = 0

table_defaults = {}
conditions = ['saccade', 'keypress']
default_condition = None

#########################################
# Development Mode Settings
#########################################
dm_auto_threshold = True
dm_trial_show_mouse = True
dm_ignore_local_overrides = False
dm_show_gaze_dot = True
dm_offset_size = 5

#########################################
# Data Export Settings
#########################################
primary_table = "trials"
unique_identifier = "userhash"
exclude_data_cols = ["created"]
append_info_cols = ["random_seed"]
datafile_ext = ".txt"

# These were include in a old version of a prior (but linked) experiment.
# While I'm not sure (yet) of their purpose, they're included for posterity's sake
# Not sure if these are vestigial from older version of KLibs
default_participant_fields = [[unique_identifier, "participant"], "gender", "age", "handedness"]
default_participant_fields_sf = [[unique_identifier, "participant"], "random_seed", "gender", "age", "handedness"]

