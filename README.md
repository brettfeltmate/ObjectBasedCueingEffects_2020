# ObjectBasedCueingEffects_2020

ObjectBasedCueingEffects is an experiment program for a study exploring whether the attentional phenomenon of 'inhibition of return' (IOR) is due to inhibition for locations in space or inhibition for objects. In this experiment, one end of one of two placeholder boxes (long or wide rectangles) is cued. Following that a target is presented either at the cued location (same side, same box), the cued object (other side, same box), 'adjacent uncued object' (same side, other box), or 'opposite uncued object' (other side, other box). 

The experiment also compares performance in the different cue-target conditions between when participants are asked to respond to targets by making saccades towards them (the **saccade** condition) and when participants are asked to make a speeded detection response for them via the keyboard without moving their eyes (the **keypress** condition).

## Requirements

ObjectBasedCueingEffects_2020 is programmed in Python 2.7 using the [KLibs framework](https://github.com/a-hurst/klibs). It has been developed and tested on macOS (10.10 through 10.13), but should also work with minimal hassle on computers running [Ubuntu](https://www.ubuntu.com/download/desktop) or [Debian](https://www.debian.org/distrib/) Linux. It is not currently compatible with any version of Windows, nor will it run under the [Windows Subsystem for Linux](https://msdn.microsoft.com/en-us/commandline/wsl/install_guide).

The experiment is designed to be run with an EyeLink eye tracker, but it can be downloaded and tested without one (using the mouse cursor as a stand-in for gaze position) by adding the flag `-ELx` to the `klibs run` command.

## Getting Started

### Installation

First, you will need to install the KLibs framework by following the instructions [here](https://github.com/a-hurst/klibs).

Then, you can then download and install the experiment program with the following commands (replacing `~/Downloads` with the path to the folder where you would like to put the program folder):

```
cd ~/Downloads
git clone https://github.com/brettfeltmate/ObjectBasedCueingEffects_2020.git
```

If you intend to run this experiment with an EyeLink eye tracker, you will also need to install the EyeLink Developer's Kit for your OS (available on the SR Support forums [here](https://www.sr-support.com/forum/downloads/eyelink-display-software)) and make sure the 'pylink' module has been properly installed.

### Running the Experiment

ObjectBasedCueingEffects_2020 is a KLibs experiment, meaning that it is run using the `klibs` command at the terminal (running the 'experiment.py' file using python directly will not work).

To run the experiment, navigate to the ObjectBasedCueingEffects_2020 folder in Terminal and run `klibs run [screensize]`,
replacing `[screensize]` with the diagonal size of your display in inches (e.g. `klibs run 24` for a 24-inch monitor). If you just want to test the program out for yourself and skip demographics collection, you can add the `-d` flag to the end of the command to launch the experiment in development mode.

#### Optional Settings

In the experiment, participants are placed into one of two response conditions: the **keypress** conditon, where they respond to targets using the space bar while keeping their eyes in the middle of the screen, or the **saccade** condition, where they respond to targets by making saccades towards them.

To choose which condition to run, launch the experiment with the `--condition` or `-c` flag, followed by either `keypress` or `saccade`. For example, if you wanted to run the saccade response condition on a computer with a 19-inch monitor, you would run 

```
klibs run 19 --condition saccade
```

If no condition is manually specified, the experiment program defaults to running the keypress response condition.

### Exporting Data

To export data from ObjectBasedCueingEffects_2020, simply run 

```
klibs export
```
while in the ObjectBasedCueingEffects_2020 directory. This will export the trial data for each participant into individual tab-separated text files in the project's `ExpAssets/Data` subfolder. If you want to export the trial error data (a log of the trials on which participants made an error that caused the trial to be recycled) or the saccade data (the saccades that participants made on each trial), you can similarly export those using 

```
klibs export -t trials_err  # for trial error data
klibs export -t saccades  # for saccade data
```
