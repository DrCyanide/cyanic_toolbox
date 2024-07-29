# Cyanic Toolbox
This Blender Add-on allows for you to quickly make a 3D face mesh from a 2D image, touch up that face mesh, and align Rigify bones to it.

## Install
* Download the project as a zip file, and put it in the directory of your choosing
* DO NOT UNZIP IT! Blender add-ons like to be zipped up
* Open Blender with "Run as administrator" to be able to install the dependencies. (You can open it normally if you're using the portable version of Blender)
* Edit > Preferences > Add-ons > Install, then navigate to the saved zip folder
* Search for "Cyanic Toolbox" and check the box next to it, then click the triangle to expand the add-on preferences
* Click either the "Install all dependencies" button, or go one by one down the dependencies to install them
* Once all the dependencies are installed, `Cyanic` should show up in your Layout's sidebar menu

## Use
* In the "Facemesh Builder" section, select the filepath for an image with a face - ideally a JPG but sometimes PNGs have the correct formatting to work
* Click the "Create face mesh" button
* The generated .obj will be automatically imported into the scene. By default, this generated file (and it's texture) are saved in the same directory as your source image
* Cleanup tools like "Open eyes" and "Open mouth" can make it easier for adding higher quality 3D eyes/teeth
* "Snap to Symmetry" is easy access to the Blender function with the same name. Sometimes it works great, other times it needs some help
* "Undo" and "Redo" commands should work as expected
* The "Rig Face + Eyes" will align Rigify Meta-rig bones with their closest matching vertex in the face mesh. IT DOES NOT PARENT ANYTHING! That has to be done after you generate a rig from the meta-rig.

## MOCAP DOES NOT WORK YET

Mediapipe 3D Pose Estimation from 2D image/video is highly desirable feature, but it takes a lot of math that I need to study before I can make it a reality. The Work In Progress Mocap tab is there if you want to play with it, but don't expect much.
