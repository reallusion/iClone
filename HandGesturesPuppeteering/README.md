# Hand Gestures Puppeteering

### Version: 2.0.0

1. Fixed blending errors between the gesture points.
2. Removed influence on the movement of the wrists.
3. Three completely new presets: "Standard", "Male", and "Female".
4. The UI will now store the state of the prior session.
5. The UI can now return the default factory state, with a press of a button.
6. Now supports transitioning between the end of the recorded clip and any existing clip in the timeline.
7. End transition period can be adjusted (number of transition frames).

### Version: 1.2.0

Additional enhancements, see Release Notes.

### Version: 1.1.0

Various bug fixes and enhancements, see Release Notes.

### Version: 1.0.0

Various enhancements, see Release Notes.

### Version: 0.9.0

Official Release

### Introduction

Hand Gestures Puppeteering can be used to rig an avatar's fingers and blend their movements among several key poses.

### Installation

1. Clone or download the Reallusion/iClone GitHub.
2. Copy **HandGesturesPuppeteering** folder into the iClone install directory > **...\Bin64\OpenPlugin**.
3. Load the script into the project from the menu: **Plugins > Python Samples > Hand Gestures Puppeteering**.

### Release Notes

Please see the CHANGES.current file for a detailed list of bug fixes and
new features for the current release. The CHANGES file contains bug fixes
and new features for older versions.

### Known Issues

1. Sometimes hand motion capture will erase existing motion clips in the timeline.

2. Gesture adjustment will have a tendency to deviate from the current hand gesture (data inaccuracy). 
    This affects the following features:
        - Replace with Right Hand Gesture
        - Replace with Left Hand Gesture

3. The capture position will snap immediately to the cursor position when a pen tablet is used. Therefore, the transition time can not be controlled like with a mouse.

### iClone API Update date: 20181204.1


 -- Reallusion Maintainers
