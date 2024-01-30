# pyright: reportMissingImports=false
import FreeCAD as App
#import FreeCADGui as Gui
#import json
import math
from FreeCAD import Base

#import dactyl_manuform_freecad
from .dmkb_keyplate import ParametricKeyPlate

# Function to convert degrees to radians
def deg_to_rad(deg):
    return deg * math.pi / 180


# Function to create a transformation matrix for a single joint
#this should return freeCAD Placements
def create_transformation(length, angle):
    # Convert angle to radians - not needed
    #angle_rad = deg_to_rad(angle)

    # Create rotation
    rotation = Base.Rotation(Base.Vector(1, 0, 0), -angle)

    # Rotate the translation vector
    translation = Base.Vector(0, length, 0)
    rotated_translation = rotation.multVec(translation)

    # Combine translation and rotation into a transformation matrix
    place = App.Placement()
    place.Base = rotated_translation
    place.Rotation = rotation   
    
    return place

def makeKey(name = "Key_Plate"):
    # example keyplate
    myObj = App.ActiveDocument.addObject("Part::FeaturePython", name)
    ParametricKeyPlate(myObj)
    myObj.ViewObject.Proxy = 0  # This is mandatory unless we code the ViewProvider too.
    
    #App.ActiveDocument.recompute()
    
    return myObj
    
    

def create_Rotated_kps(finger_data):
    # JSON Data read moved to fractyl parent macro
    #filepath = r"C:\Users\mbarr\OneDrive\Documents\01. Projects\05_3D_Printing\KEYBOARD\HandPose\fdata3.json"
    App.Console.PrintMessage("Generating Keyplates for Finger Measurement Data"+"\n")


    ROT90X = Base.Rotation(Base.Vector(1, 0, 0), 90)
    origin = Base.Vector(0,0,0)
    rot90x = App.Placement(origin,ROT90X) #origin)
    # JSON Data read moved to fractyl parent macro
    # Read JSON data
    #with open(filepath, 'r') as file:
    #    finger_data = json.load(file)

    keyrows = ['top','middle', 'bottom']

    # Create transformations and apply them to an object
    for row in keyrows:
        knuckle_offset = App.Placement(Base.Vector(20,0,0), Base.Rotation(0,0,0))
        for finger in finger_data:
           
            #print(finger_data[finger]["Knuckle_Offset"])
            placeholder_object = makeKey(name = finger+'_'+row) #App.ActiveDocument.addObject("Part::Box", finger+'_'+row)

            placeholder_object.Placement = knuckle_offset
            knuckle_offset.move(Base.Vector(20,0,0))
            

            for joint in finger_data[finger]:
                joint_data = finger_data[finger][joint]
                
                if row == 'top':

                    # Apply neutral/middle position transformation
                    neutral_matrix = create_transformation(joint_data["Length"], joint_data["Angle Start"]) 
                    placeholder_object.Placement = placeholder_object.Placement.multiply(neutral_matrix)
                    
                    #placeholder_object.Shape.transformShape(neutral_matrix)
                    App.ActiveDocument.recompute()
                    
                if row == 'middle':
                    # Apply middle position transformation
                    mid_matrix = create_transformation(joint_data["Length"], (joint_data["Angle Start"]+joint_data["Angle End"])/2) 
                    placeholder_object.Placement = placeholder_object.Placement.multiply(mid_matrix)
                    
                    #placeholder_object.Shape.transformShape(neutral_matrix)
                    App.ActiveDocument.recompute()
                
                
                if row == 'bottom':
                    # Maximum finger rotation
                    mid_matrix = create_transformation(joint_data["Length"], joint_data["Angle End"]) 
                    placeholder_object.Placement = placeholder_object.Placement.multiply(mid_matrix)
                    
                    #placeholder_object.Shape.transformShape(neutral_matrix)
                    App.ActiveDocument.recompute()

                # Create maximum angle and maximum extension objects (as examples)
                #max_angle_object = App.ActiveDocument.addObject("Part::Box", finger + "_" + joint + "_MaxAngle")
                #max_angle_matrix = create_transformation(joint_data["Length"], joint_data["Angle End"])
                #max_angle_object.Placement = App.Placement(max_angle_matrix)

                #max_extension_object = App.ActiveDocument.addObject("Part::Box", finger + "_" + joint + "_MaxExtension")
                #max_extension_matrix = create_transformation(joint_data["Length"], joint_data["Angle Start"])
                #max_extension_object.Placement = App.Placement(max_extension_matrix)
            placeholder_object.Placement = placeholder_object.Placement.multiply(rot90x)
    
    return None

