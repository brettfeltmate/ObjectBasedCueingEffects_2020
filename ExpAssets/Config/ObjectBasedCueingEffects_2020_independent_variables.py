from klibs.KLIndependentVariable import IndependentVariableSet
from klibs import P

ObjectBasedCueingEffects_2020_ind_vars = IndependentVariableSet()

ObjectBasedCueingEffects_2020_ind_vars.add_variable('box_alignment', str)
ObjectBasedCueingEffects_2020_ind_vars.add_variable('cue_location', str)
ObjectBasedCueingEffects_2020_ind_vars.add_variable('target_location', str)

ObjectBasedCueingEffects_2020_ind_vars['box_alignment'].add_values('horizontal', 'vertical')
ObjectBasedCueingEffects_2020_ind_vars['cue_location'].add_values('top_left', 'top_right', 'bottom_left', 'bottom_right')
ObjectBasedCueingEffects_2020_ind_vars['target_location'].add_values('cued_location', 'cued_object', 'uncued_adjacent', 'uncued_opposite')

if P.condition == 'keypress':
    ObjectBasedCueingEffects_2020_ind_vars['target_location'].add_value('catch')