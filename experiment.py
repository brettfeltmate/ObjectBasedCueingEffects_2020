# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLExceptions import TrialException
from klibs.KLConstants import EL_SACCADE_END, EL_FALSE, NA, RC_KEYPRESS, CIRCLE_BOUNDARY, TIMEOUT, STROKE_CENTER
from klibs.KLUtilities import deg_to_px, flush, iterable, smart_sleep, boolean_to_logical, pump
from klibs.KLUtilities import line_segment_len as lsl
from klibs.KLKeyMap import KeyMap
from klibs.KLUserInterface import key_pressed
from klibs.KLGraphics import fill, flip, blit, clear
from klibs.KLGraphics.KLDraw import Rectangle, Circle, SquareAsterisk, FixationCross
from klibs.KLCommunication import any_key, message
from klibs.KLBoundary import BoundaryInspector
from klibs.KLDatabase import EntryTemplate

from math import pi, cos, sin
from sdl2 import SDLK_SPACE

import numpy as np
from PIL import Image, ImageDraw
import aggdraw

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)

TOP_LEFT = "top_left"
TOP_RIGHT = 'top_right'
BOTTOM_LEFT = 'bottom_left'
BOTTOM_RIGHT = 'bottom_right'

SACC_INSIDE = "inside"
SACC_OUTSIDE = "outside"

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'



class ObjectBasedCueingEffects_2020(klibs.Experiment):
    # trial data
    saccades = []
    target_acquired = False

    def setup(self):

        # Generate messages to be displayed during experiment
        self.err_msgs = {}
        if P.saccade_response_cond:
            self.err_msgs['eye'] = "Moved eyes too soon!"
            self.err_msgs['key'] = "Please respond with eye movements only."
            self.err_msgs['early'] = self.err_msgs['key']  # for convenience in logic
        else:
            self.err_msgs['eye'] = "Moved eyes!"
            self.err_msgs['key'] = "Please respond with the spacebar only."
            self.err_msgs['early'] = "Responded too soon!"

        # Stimulus sizes
        self.target_diameter = deg_to_px(1.0)

        self.cue_seg_len = deg_to_px(1.7)
        self.cue_seg_thick = deg_to_px(0.4)

        self.rect_long_side = deg_to_px(11.4)
        self.rect_short_side = deg_to_px(1.7)
        self.rect_thickness = deg_to_px(0.2)

        self.fix_width = deg_to_px(1.0)
        self.fix_thickness = deg_to_px(0.2)

        # Stimulus drawbjects
        # NOTE: too many properties of placeholders & cue vary trial-by-trial, easier to construct during trial_prep()
        self.fix = FixationCross(size=self.fix_width, thickness=self.fix_thickness, fill=RED)
        self.target = Circle(diameter=self.target_diameter, fill=WHITE)

        # Offset between center of placeholders & fixation
        offset = deg_to_px(4.8)

        # Use offsets to establish possible stimulus locations
        self.locations = {
            "left": [P.screen_c[0] - offset, P.screen_c[1]],
            'right': [P.screen_c[0] + offset, P.screen_c[1]],
            'top': [P.screen_c[0], P.screen_c[1] - offset],
            'bottom': [P.screen_c[0], P.screen_c[1] + offset],
            'top_left': [P.screen_c[0] - offset, P.screen_c[1] - offset],
            'top_right': [P.screen_c[0] + offset, P.screen_c[1] - offset],
            'bottom_left': [P.screen_c[0] - offset, P.screen_c[1] + offset],
            'bottom_right': [P.screen_c[0] + offset, P.screen_c[1] + offset]
        }

        # Define keymap for ResponseCollector
        self.keymap = KeyMap(
            "speeded response",  # Name
            ["spacebar"],  # UI Label
            ["spacebar"],  # Data Label
            [SDLK_SPACE]  # SDL2 Keycode
        )

        # Instantiate boundary inspector to handle drift checks & target acquisitions (for saccade responses)
        self.bi = BoundaryInspector()
        self.gaze_boundary = deg_to_px(3.0)  # Radius of 3.0º of visual angle
        self.bi.add_boundary(label="drift_correct", bounds=[P.screen_c, self.gaze_boundary], shape="Circle")

    def block(self):

        block_num = P.block_number
        block_count = P.blocks_per_experiment

        # Display progress messages at start of blocks
        if block_num > 1:
            flush()
            fill()
            block_msg = "Completed block {0} of {1}. Press any key to continue."
            block_msg = block_msg.format(block_num - 1, block_count)
            message(block_msg, registration=5, location=P.screen_c)
            flip()
            any_key()

    def setup_response_collector(self):
        self.rc.uses(RC_KEYPRESS)
        self.rc.end_collection_event = "task_end"
        self.rc.display_callback = self.display_refresh
        self.rc.display_kwargs = {'target': True}
        self.rc.keypress_listener.key_map = self.keymap
        self.rc.keypress_listener.interrupts = True

    def trial_prep(self):

        if P.development_mode:
            print "\ntrial factors"
            print "======================"

            fill()
            msg = "Box Alignment: {0}\nCue Location: {1}\nTarget Location: {2}".format(
                self.box_alignment, self.cue_location, self.target_location)
            print msg
            print "======================"
            message(msg, registration=5, location=P.screen_c, blit_txt=True)
            flip()

            any_key()

            clear()
            any_key()


        self.placeholder = self.construct_placeholder()
        self.cue = self.construct_cue()

        self.cue_loc = self.locations[self.cue_location]

        self.set_box_positions()

        self.target_trial = False

        if self.target_location != 'catch':
            self.target_trial = True
            self.target_loc = self.get_target_location()

        self.evm.register_tickets([
            ('cue_on', 1000),       # Cue appears 1000ms after drift check
            ('cue_off', 1100),      # Cue removed after 100ms
            ('target_on', 1960),    # Target appears 860ms after cue removal
            ('task_end', 4460)     # 2500ms to respond to target before trial aborts
        ])

        # Reset trial flags
        self.before_target = True
        self.target_acquired = False
        self.moved_eyes_during_rc = False

        self.display_refresh()
        self.el.drift_correct(fill_color=BLACK, draw_target=EL_FALSE)
        self.fix.fill = WHITE
        self.display_refresh()
        flush()

    def trial(self):


        while self.evm.before('cue_on'):
            self.wait_time()

        self.display_refresh(cue=True)

        while self.evm.before('cue_off'):
            self.wait_time()


        self.display_refresh()

        while self.evm.before('target_on'):
            self.wait_time()

        flush()

        self.display_refresh(target=True)

        if P.saccade_response_cond:
            self.record_saccades()
            keypress_rt = 'NA'

        if P.keypress_response_cond:
            self.rc.collect()
            keypress_rt = self.rc.keypress_listener.response(rt=True, value=False)

        clear()
        smart_sleep(1000)

        if P.keypress_response_cond:
            if self.target_location == "catch" and keypress_rt != TIMEOUT:
                fill()
                message(self.err_msgs['early'], registration=5, location=P.screen_c)
                flip()
                any_key()
            elif self.moved_eyes_during_rc:
                fill()
                message("Moved eyes during response interval!", registration=5, location=P.screen_c)
                flip()
                any_key()

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            'session_type': 'saccade' if P.saccade_response_cond else 'keypress',
            'box_alignment': self.box_alignment,
            'cue_location': self.cue_location,
            'target_location': self.target_location,
            'target_acquired': str(self.target_acquired).upper() if P.saccade_response_cond else NA,
            'keypress_rt': keypress_rt if P.keypress_response_cond else NA,
            'moved_eyes': str(self.moved_eyes_during_rc).upper() if P.keypress_response_cond else NA

        }


    def trial_clean_up(self):
        if P.trial_id and P.saccade_response_cond:  # won't exist if trial recycled
            for s in self.saccades:
                trial_template = EntryTemplate('saccades')
                s['trial_id'] = self.db.last_id_from('trials')
                s['participant_id'] = P.participant_id
                for f in s:
                    if f == "end_time":
                        continue
                    trial_template.log(f, s[f])
                self.db.insert(trial_template)
        self.saccades = []
        self.target_acquired = False

        self.fix.fill = RED



    def clean_up(self):
        pass

    def display_refresh(self, cue=False, target=False):
        # In keypress condition, after target presented, check that gaze
        # is still within fixation bounds and print message at end if not
        if P.keypress_response_cond and not self.before_target:

            gaze = self.el.gaze()
            if not self.bi.within_boundary(label='drift_correct', p=gaze):
                self.moved_eyes_during_rc = True

        fill()

        blit(self.fix, registration=5, location=P.screen_c)

        blit(self.placeholder, registration=5, location=self.box1_loc)
        blit(self.placeholder, registration=5, location=self.box2_loc)

        if cue:
            blit(self.cue, registration=5, location=self.cue_loc)

        if target:
            if self.target_location != 'catch':
                blit(self.target, registration=5, location=self.target_loc)

            if self.before_target:
                self.before_target = False

        flip()

    def set_box_positions(self):

        if self.box_alignment == VERTICAL:
            self.box1_loc = self.locations['left']
            self.box2_loc = self.locations['right']

        else:
            self.box1_loc = self.locations['top']
            self.box2_loc = self.locations['bottom']

    def get_target_location(self):

        box1 = None
        box2 = None

        if self.box_alignment == VERTICAL:

            box1 = [self.locations['top_left'], self.locations['bottom_left']]
            box2 = [self.locations['top_right'], self.locations['bottom_right']]

        else:
            box1 = [self.locations['top_left'], self.locations['top_right']]
            box2 = [self.locations['bottom_left'], self.locations['bottom_right']]


        if self.target_location == 'cued_location':
            target_loc = self.cue_loc

        if self.target_location == 'cued_object':

            target_box = self.which_list(self.cue_loc, True, box1, box2)
            target_box.remove(self.cue_loc)
            target_loc = target_box[0]

        else:
            target_box = self.which_list(self.cue_loc, False, box1, box2)

            if self.target_location == 'uncued_adjacent':

                if self.box_alignment == HORIZONTAL:

                    target_loc = self.which_list(self.cue_loc[0], True, target_box[0], target_box[1])
                else:

                    target_loc = self.which_list(self.cue_loc[1], True, target_box[0], target_box[1])

            else:

                if self.box_alignment == HORIZONTAL:

                    target_loc = self.which_list(self.cue_loc[0], False, target_box[0], target_box[1])

                else:

                    target_loc = self.which_list(self.cue_loc[1], False, target_box[0], target_box[1])


        return target_loc

    def construct_placeholder(self):
        stroke = [self.rect_thickness, WHITE, STROKE_CENTER]
        # width = None
        # height = None

        # Horizontal/vertical indicates directionality of placeholders length
        if self.box_alignment == VERTICAL:
            width, height = self.rect_short_side, self.rect_long_side

        else:
            height, width = self.rect_short_side, self.rect_long_side

        return Rectangle(width=width, height=height, stroke=stroke)

    def construct_cue(self):

        self.cue_seg_len = deg_to_px(1.7)
        self.cue_seg_thick = deg_to_px(0.4)

        canvas_size = [self.cue_seg_len, self.cue_seg_len]

        canvas = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        surface = aggdraw.Draw(canvas)

        pen = aggdraw.Pen(WHITE, self.cue_seg_len)

        # Regardless of orientation, two segments remain the same
        xy = [(0, 0, 0, self.cue_seg_len), (0, 0, self.cue_seg_len, 0)]

        # Add missing segment, dependent on orientation
        if self.box_alignment == VERTICAL:
            xy.append((self.cue_seg_len, self.cue_seg_len, 0, self.cue_seg_len))

        else:
            xy.append((self.cue_seg_len, 0, self.cue_seg_len, self.cue_seg_len))

        for seg in xy:
            surface.line(seg, pen)

        surface.flush()

        return np.asarray(canvas)

    def which_list(self, x, contains, l1, l2):

        if x in l1:
            return l1 if contains else l2
        elif x in l2:
            return l2 if contains else l1
        else:
            print "element not in either list"
            return None

    def log_and_recycle_trial(self, err_type):
        """
        Renders an error message to the screen and wait for a response. When a
        response is made, the incomplete trial data is logged to the trial_err
        table and the trial is recycled.

        """
        flush()
        fill()
        message(self.err_msgs[err_type], registration=5, location=P.screen_c)
        flip()
        any_key()
        err_data = {
            "participant_id": P.participant_id,
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "session_type": 'saccade' if P.saccade_response_cond else 'keypress',
            "cue_location": self.cue_location,
            "target_location": self.target_location,
            "box_alignment": self.box_alignment,
            "err_type": err_type
        }
        self.database.insert(data=err_data, table="trials_err")
        raise TrialException(self.err_msgs[err_type])

    def wait_time(self):
        # Appropriated verbatim from original code written by John Christie
        if self.before_target:
            gaze = self.el.gaze()
            if not self.bi.within_boundary(label='drift_correct', p=gaze):
                self.log_and_recycle_trial('eye')
            q = pump(True)
            if key_pressed(queue=q):
                if key_pressed(SDLK_SPACE, queue=q):
                    self.log_and_recycle_trial('early')
                else:
                    self.log_and_recycle_trial('key')

    def record_saccades(self):
        # Following code a rehashing of code borrowed from John Christie's original code

        # Get & write time of target onset
        target_onset = self.el.now()
        self.el.write("TARGET_ON %d" % target_onset)

        # Until 2500ms post target onset, or until target fixated
        while self.el.now() - 2500 and not self.target_acquired:
            self.display_refresh(target=True)
            pump()
            # Get end point of saccades made
            queue = self.el.get_event_queue([EL_SACCADE_END])
            # Check to see if saccade was made to target
            for saccade in queue:
                # Get end point of saccade
                gaze = saccade.getEndGaze()
                # Check if gaze fell outside fixation boundary
                if lsl(gaze, P.screen_c) > self.gaze_boundary:
                    # Get distance between gaze and target
                    dist_from_target = lsl(gaze, self.target_loc)
                    # Log if saccade is inside or outside boundary around target
                    accuracy = SACC_OUTSIDE if dist_from_target > self.gaze_boundary else SACC_INSIDE

                    # If more than one saccade
                    if len(self.saccades):
                        # Grab duration of saccade, relative to the previous saccade
                        # Not entirely sure why 4 is added....
                        duration = saccade.getStartTime() + 4 - self.saccades[-1]['end_time']
                    # Otherwise, get duration of saccade relative to target onset
                    else:
                        duration = saccade.getStartTime() + 4 - target_onset

                    # Write saccade info to database
                    if len(self.saccades) < 3:
                        self.saccades.append({
                            "rt": saccade.getStartTime() - target_onset,
                            "accuracy": accuracy,
                            "dist_from_target": dist_from_target,
                            "start_x": saccade.getStartGaze()[0],
                            "start_y": saccade.getStartGaze()[1],
                            "end_x": saccade.getEndGaze()[0],
                            "end_y": saccade.getEndGaze()[1],
                            "end_time": saccade.getEndTime(),
                            "duration": duration
                        })

                    # Target found = True if gaze within boundary surrounding target
                    if dist_from_target <= self.gaze_boundary:
                        self.target_acquired = True
                        break
