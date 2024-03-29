import FreeCAD as App
import Part
#import Base
from FreeCAD import Base
#from .topology import *

####
# Rotate the keypad to the desired tenting angle.
# Fuse solid features if needed.
####

#pth = "C:\\Users\\mbarr\\OneDrive\\Documents\\01. Projects\\03_SW_Dev\\Fractyl\\src\\Fractyl"
#filename = "Rotate_Tent.py"
#exec(open(pth + "\\" + filename).read())
wrist_angle = 60 # degrees
keyrows = ['top','middle','bottom']
fingers = ['point', 'index', 'ring', 'pinky']

keyname = "Fusion_Keys" # TODO: use some manner of user naming at this stage?

def Fuse_Objects():
    # Get all objects that are solid
    # Fuse them.
    # getattr(shp,"ShapeType",None)
    doc = App.activeDocument()
    objects = doc.Objects
    App.Console.PrintMessage(f"\nAll Objects:\n{objects}\n---\n")

    # Key plates are 'compound', as are fusions in general
    solid_objects = []   #obj for obj in objects if hasattr(obj, 'PlateType') or hasattr(obj,'ShapeType') ]
    for obj in objects:
        if hasattr(obj, 'Shape'): 
            shptype = getattr(obj.Shape,'ShapeType',None)
            if shptype is not None:
                App.Console.PrintMessage(f"\n{obj.Label}\n{obj}\n{shptype}")
                solid_objects.append(obj)
            else:
                App.Console.PrintMessage(f"\n{obj.Label} Has No Shape Type\n{obj}")
        else:
            App.Console.PrintMessage(f"\n{obj.Label} Is not a Shape\n{obj}")
        
    count = len(solid_objects)
    App.Console.PrintMessage(f"\nAdded {count} objects to fuse list\n")

    #shape_list = [obj.Shape for obj in solid_objects] 


    if count > 1:
        # From: https://forum.freecad.org/viewtopic.php?t=4137
        
        # dict of lists of columns
        column_obj_dict = { str(col): [] for col in fingers}
        #fill_obj_list = [] # Not needed for MultiFuse
        # grab items in a given column
        for obj in solid_objects:
            # Check Label against column names, store index
            labelstr = obj.Label.split('_')
            try:
                # if label is in fingers
                column_obj_dict[labelstr[0]].append(obj)
                # no need to append to fill obj list seperately, handled by naming solids
                #fill_obj_list.append(obj)
            except KeyError:
                App.Console.PrintMessage(f"\n{labelstr[0]} not found in column list\n")
                #if labelstr[0] == "ColumnFill" and labelstr[1] == "solid":
                #    fill_obj_list.append(obj)
                continue
        
        # Fuse each column seperately. Then fuse column fill solid objects in order
        #fused_cols = []
        newShapeList = []
        fusion = App.activeDocument().addObject("Part::MultiFuse",keyname)#"Whole_MultiFuse")
        for col in fingers:
            
            obj_list = column_obj_dict[col]
            #newShape = obj_list.pop(0).Shape
            #newShapeList = [obj_list.pop(0)] # not needed if we arent piggybacking on .fuse
            # newShapeList = [] # removing - attempting to MultiFuse everything
            #fusion = App.activeDocument().addObject("Part::MultiFuse",col+"_fuse")
            #App.activeDocument().Fusion.Shapes = [App.activeDocument().Tube,App.activeDocument().Box,]
            
            for i in obj_list:
                if i.isDerivedFrom("Part::Feature"):
                    newShapeList.append(i)
                    App.Console.PrintMessage(f"\n{i.Label} added to fuse for {col}\n")
                    #newShape = newShape.fuse(i.Shape) # note: MultiFuse is deprecated, use fuse
                    #i.Visibility = False
            
            #fusion.Shapes = newShapeList
            # Add column fill
            # Not needed since we are naming the solid fill and including in multifuse
            # if len(fill_obj_list) > 0:
            #     #newShape = newShape.fuse(fill_obj_list.pop(0).Shape)
            #     newShapeList.append(fill_obj_list.pop(0))
            #newObject = App.ActiveDocument.addObject("Part::Feature",col+"_fuse")
            #newObject.Shape = newShape
            
            # fusion.Shapes = newShapeList            
            # doc.recompute()
            # fusion.purgeTouched() # Maybe?
            # fused_cols.append(fusion)
            # #fused_cols.append(newObject)
            # doc.recompute()
        fusion.Shapes = newShapeList
        doc.recompute()

        # Use MultiFuse as above
        App.Console.PrintMessage(f"Fusing Whole\n Using MultiFuse\n")
        #whole_fusion = App.activeDocument().addObject("Part::MultiFuse","Whole_Fuse")
        #whole_fusion.Shapes = fused_cols # Must be document objects
        
        # Repeat for new fused columns
        #App.Console.PrintMessage(f"\nFusing Whole\n\n{fingers[0]} is initial shape for whole \n")
        #newShape = fused_cols.pop(0).Shape
        #App.Console.PrintMessage(f"\nSeed Shape is:{newShape} - {type(newShape)} -\n")
        #newShape.Visibility = False
        # for i in fused_cols:
        #     App.Console.PrintMessage(f"\nFusing {i.Label} to whole (type: {type(i)} )\n")
        #     if i.isDerivedFrom("Part::Feature"):
        #         newShape = newShape.fuse(i.Shape) 
        #         i.Visibility = False
        #newObject = App.ActiveDocument.addObject("Part::Feature","whole_fuse")
        #newObject.Shape = newShape
        #doc.recompute()

    else:
        App.Console.PrintMessage("\n\nError: did not collect objects\n\n")

    return count

def Rotate_Object(angle = wrist_angle):
    """ Defaults to constant wrist_angle. In degrees"""
    doc = App.activeDocument()
    # Create rotation: about Y, angle in Degrees, Right-Hand Rule
    rotation = Base.Rotation(Base.Vector(0, 1, 0), angle)

    obj = doc.getObject(keyname) # currently the constant name of the whole multifuse

    place = App.Placement()
    #place.Base = rotated_translation # Can Also Translate when/if needed
    place.Rotation = rotation 

    obj.Placement = obj.Placement.multiply(place)

    doc.recompute()



if __name__ == "__main__":
    numfused = Fuse_Objects()
    App.Console.PrintMessage(f"\nFused {numfused} objects\n")
    #Rotate_Object(wrist_angle)
