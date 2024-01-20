# pyright: reportMissingImports=false
import FreeCAD as App
from FreeCAD import Base

#import Rotate_To_Fingers as rf
from .Solid_From_Points import GenerateSolid

####
# We will need to access the active document 
# and get already create objects for reference
# Refernce: https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Code_snippets.md
####

doc = App.ActiveDocument
objs = doc.Objects 

# Unit-ish vector for testing
unitBoxVec = [ [0.0, 0.0, 0.0],[2.0, 0.0, 0.0], [2.0, 1.0, 0.0], [0.0, 1.0, 0.0],[0.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0]]

# Keyrows and fingers - hard coded for now
# 18 Jan 2024: Pass as input from Fractyl Macro
#keyrows = ['top','middle','bottom']
#fingers = ['point', 'index', 'ring', 'pinky']

####
# Helper functions
####

####
# generate lists of text for object and vertex lists
####

# Get list of object labels from doc
def getDocObjectNameList():
    # we'll start by just getting objects in the file
    # and assume for now that we've had complete control of the file
    
    names = []
    
    for obj in objs:
        names.append(obj.Label)
    
    return names

# Generate Object Labels from keyrow and finger lists
def genObjectNames(keyrows, fingers):
    
    names = []
    
    for digit in fingers:
        for row in keyrows:
            names.append(digit+'_'+row)
    
    return names
    
# Generate vertex names for sides known to be facing each other
#TODO: use face normals to find or check for facing condition
def genVertexNames():
    # Solid creation from points proceeds in specific order
    # requires left-most bottom vertex first
    # must proceed counter clockwise around bottom
    # then same order for top
    # front and back of each keyplate keeps the same labeling in testing.
    # So, only one list of vertices is needed, and the set of keys 
    # they are selected from must change in the selecting obj func.
    
    ptidx_list = ['4','12','7','3','2','5','6','1'] #str for clarity
    names = []
    for pt in ptidx_list:
        names.append('Vertex'+pt)
    
    return names

# Now, we can grab ojbects
# We should proceed down a single column first, i.e. by Finger
# Solid_from_points considers the first 4 vtx's the 'bottom', second 4 the 'top'
# we'll try to keep that terminology here.
# We'll assume we are given names of a top key obj, and a bottom key obj
def genVecList(topkey, botkey):
    # TODO: Verify that we are using the right objects
    # botkey.PlateType == 'UNDERCUT'
    
    vertlist = []
    bottom = doc.getObject(botkey)
    top = doc.getObject(topkey)
    pts = genVertexNames()
    
    for i, pt in enumerate(pts):
        if i < 4:
            vertlist.append(bottom.getSubObject(pt))
        else:
            vertlist.append(top.getSubObject(pt))
            
    # We need vectors for 'Solid...', so create those from vertexes
    VecList = []
    for v in vertlist:
        VecList.append(Base.Vector(v.X,v.Y,v.Z))
    
    return VecList
    
####
# Geometry creation
####

# Proceed filling gaps in each finger column
# by identifying the row above gap and below gap to be filled     
# pass full key name/label to helper functions to generate veclist
# then create the geometry with the given veclist. move to nxt. repeat
def FillWeb(keyrows, fingers):
    names = []
    
    for digit in fingers:
        
        numgaps = len(keyrows) - 1
        
        for i in range(numgaps):
            topname = digit+'_'+keyrows[i]
            botname = digit+'_'+keyrows[i+1]
            
            myVecList = genVecList(topname,botname)
            
            myObj = doc.addObject("Part::FeaturePython", digit+'_web_'+str(i))
            GenerateSolid(myObj, myVecList)
            myObj.ViewObject.Proxy = 0 # not coding viewprovider
            App.ActiveDocument.recompute()


if __name__ == '__main__':
    App.Console.PrintMessage("Running as main from Create Web")
    keyrows = ['top','middle','bottom']
    fingers = ['point', 'index', 'ring', 'pinky']
    FillWeb(keyrows,fingers)
