# Temple Run Pose Detector

Play Temple Run by moving in real life!

## Overview

This project uses MediaPipe to detect poses in real time to control the in-game Temple Run character.

## Gameplay
The project uses the following website to run Temple Run: [Temple Run Website](https://www.google.com/aclk?sa=l&ai=DChcSEwiuk4C1ruKKAxXtEq0GHUerNA0YABAAGgJwdg&ae=2&aspm=1&co=1&ase=2&gclid=CjwKCAiAm-67BhBlEiwAEVftNque3z1Ev1_c9LAF4NduLKafKqq3wvT3ItbtIqqdx4Atq4-u0L8L5BoCNZIQAvD_BwE&sig=AOD64_39T4VXYqpj2nSUJHqiHt_SIUiXCA&q&nis=4&adurl&ved=2ahUKEwjosvu0ruKKAxWGPjQIHZBAFvwQ0Qx6BAgLEAE)

You need to specify if you are playing in fullscreen mode or not. To do this, set the `-f` or `--fullscreen` argument to either `True` or `False`. It is default set to `False`. To run the game in fullscreen mode, you can run `python main.py -f True`.

Note that when you run the program, a webcam window will pop up and may take up space on your screen. You can move this window wherever you want or ignore it if playing in fullscreen mode, but it may be helpful to view at the beginning to position yourself correctly. Make sure your upper body is in view of the camera and you are centered, and don't stand too close to the camera. Also, make sure the game browser is on your current screen.

## Controls
Here are the main game controls:

* **Starting the game**: place your hands in the air so that both elbows are at around 90 degrees.
* **Moving left/right**: Move your entire body left/right in real life.
* **Jumping**: Perform a jumping jack. Make sure your hands are above your head!
* **Crouching**: Crouch down in real life.
* **Pausing**: Place your hands together in a praying pose. To unpause, perform the starting pose.
* **Quitting**: Place your arms in an "X" shape in front of your body. Note that this will quit the program entirely.

View the demo vid [here](https://drive.google.com/file/d/1N2qlYxGbu74CScLvuFnqGJNsBtNKQToa/view?usp=drive_link) for clarification.
