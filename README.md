# Fractyl - FreeCAD Native Parametric Ergo Split Keyboard

![image](https://github.com/mbarronj/Fractyl/assets/5118224/eb98037c-8ec3-4dec-a645-673475469a36)

Fractyl is a native FreeCAD Python module / macro that generates an ergonomic keyboard similar to the Dactyl and Dactyl-Manuform.

This one is based off of the Python+CadQuery port of the original Clojure+openSCAD release.
unlike the cq version, geometry is completely generated in FreeCAD with api calls, creating FreeCAD objects directly.
These are OpenCasCade geometries like CadQuery, but wrapped in FreeCAD's Pythonic API.

Instead of using the original specification JSON, Fractyl takes a different approach to specifying and designing a keyboard.
This module reads a JSON document that represents a model of a human hand, and uses that geometry to locate a (hopefully) optimal location for each keyswitch.

The hand model used is from MediaPipe's gesture recognition library.

![image](https://github.com/mbarronj/Fractyl/assets/5118224/f87054ff-5994-4614-b6b8-7b255d8dfb13)

Example hand pose estimation:

![image](https://github.com/mbarronj/Fractyl/assets/5118224/f68c1266-07c9-4770-bf2d-11b580f5d3c8)

Using MediaPipe and a webcam, I generated a basic model of my own hand to use as a seed for this keyboard design.
My original attempt did not produce the results I thought it would - It turns out a human hand can move all over the place!
So, the default_hand.json model in the repo right now has been dialed back and manually tuned somewhat.
I plan to release that python notebook in the near future, since that work is far from release at this stage. Ideally with some manner of interface, either in FreeCAD or Jupyter for entering data.


At the moment, this macro will create a new document, read the default hand model if present, and generate the Right-Hand primary key plates. It will also generate some thumb keyplates.
No base, mounting bosses, or support for the thumb is completed yet. Working on that actively.

To facilitate 3D printing and CAD file modification, the base will likely be completely seperate.

So, if you are like me and prefer a highly tented keyboard, you can print the primary face of the kb horizontally (for much better print quality), and attach it to a seperately printed base.
Then, the macro will generate a seperate base. But - you're free to use that, modify it, etc.
Let your imagination run wild - adjustable base designs, multi-color, whatever you want. It will be native FreeCAD, so it will have editable parameters directly in FreeCAD, and will be modifyable by the CAD engine like native geometry.






