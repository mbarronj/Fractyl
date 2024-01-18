import FreeCAD as App
import FreeCADGui as Gui
import json
import math
from FreeCAD import Base

#import dactyl_manuform_freecad
import dmkb_keyplate as kp

# Function to convert degrees to radians
def deg_to_rad(deg):
    return deg * math.pi / 180


# Function to create a transformation matrix for a single angle
#this should return freeCAD Placements
def create_transformation(length, angle):
    # Convert angle to radians
    angle_rad = deg_to_rad(angle)

    # Create rotation
    rotation = Base.Rotation(Base.Vector(1, 0, 0), -angle)#_rad)

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
    myObj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    kp.ParametricKeyPlate(myObj)
    myObj.ViewObject.Proxy = 0  # This is mandatory unless we code the ViewProvider too.
    
    #FreeCAD.ActiveDocument.recompute()
    
    return myObj
    
    
## Function to create a transformation matrix for a single angle
#def create_transformation_straight(length, angle):
#    # Convert angle to radians
#    angle_rad = deg_to_rad(angle)
#
#    # Create translation and rotation
#    translation = Base.Vector(0, 0, length)
#    rotation = Base.Rotation(Base.Vector(1, 0, 0), angle_rad)
#
#    # Combine translation and rotation into a transformation matrix
#    matrix = Base.Matrix()
#    matrix.move(translation)
#    matrix = matrix.multiply(rotation.toMatrix())
#    return matrix
def create_Rotated_kps():
    filepath = r"C:\Users\mbarr\OneDrive\Documents\01. Projects\05_3D_Printing\KEYBOARD\HandPose\fdata3.json"

    ROT90X = Base.Rotation(Base.Vector(1, 0, 0), 90)
    origin = Base.Vector(0,0,0)
    rot90x = App.Placement(origin,ROT90X) #origin)

    #newkey = makeKey(name='base key')


    # Read JSON data
    with open(filepath, 'r') as file:
        finger_data = json.load(file)

     # Create placeholder object for this joint
    #placeholder_object = App.ActiveDocument.addObject("Part::Box", finger + "_" + joint)
    #placeholder_object.Length = 10
    #placeholder_object.Width = 10
    #placeholder_object.Height = 10

    #knuckle_offset = App.Placement(Base.Vector(20,0,0), Base.Rotation(0,0,0))
    #placeholder_object = App.ActiveDocument.addObject("Part::Box", "test")
    #placeholder_object.Length = 18
    #placeholder_object.Width = 18
    #placeholder_object.Height = 4

    keyrows = ['middle', 'top','bottom']

    # Create transformations and apply them to an object
    for row in keyrows:
        knuckle_offset = App.Placement(Base.Vector(20,0,0), Base.Rotation(0,0,0))
        for finger in finger_data:
           
            #print(finger_data[finger]["Knuckle_Offset"])
            placeholder_object = makeKey(name = finger+'_'+row) #App.ActiveDocument.addObject("Part::Box", finger+'_'+row)
            #placeholder_object.Length = 18
            #placeholder_object.Width = 18
            #placeholder_object.Height = 4
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

    Gui.SendMsgToActiveView("ViewFit")
    return None
