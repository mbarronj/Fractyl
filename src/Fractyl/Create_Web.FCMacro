import FreeCAD as App
import FreeCADGui as Gui
import json
import math
from FreeCAD import Base
import Part

#import Rotate_To_Fingers as rf
import Solid_From_Points as sp

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
#TODO: Pass as input from higher level
keyrows = ['top','middle','bottom']
fingers = ['point', 'index', 'ring', 'pinky']

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
            sp.GenerateSolid(myObj, myVecList)
            myObj.ViewObject.Proxy = 0 # not coding viewprovider
            App.ActiveDocument.recompute()
        
# We can fill gaps between columns by offsetting inner corner points
# of each keyplate and web
keyswitch_height = 14.0
knuckle_offset = 20.0
plate_rim = 2.0
colfill_width =knuckle_offset - ( keyswitch_height + (2 * plate_rim) )
#20 - 18 = 2
'''
#TODO: Next Step: Generate column webs
# combine upper edges of column/finger geo into wire
# extrude by width
# repeat for bottom edges of next column
# connect start and end points
# make faces of side
# turn into solid
# may need a new solid making helper
def FillColumn():
    # Row Index: keyrows
    # Column Index: fingers
    # Object Label patterns: "finger_row" <- keyplate ; finger_web_# <- web
    # 
    # upper Right, Left edges: 
    # kp: Edge9, Edge2
    # web: Edge8, Edge1
    # Lower Left, Right: 
    # kp: Edge4, Edge16
    # web: Edge7, Egde5
'''    


if __name__ == '__main__':
    FreeCAD.Console.PrintMessage("Running as main from Create Web")
    FillWeb(keyrows,fingers)

"""    
myVecList = []
#for vec in unitBoxVec:
#   myVecList.append(Base.Vector(vec[0],vec[1],vec[2]))


# myObj = doc.addObject("Part::FeaturePython", "newname")
# sp.GenerateSolid(myObj, myVecList)
# myObj.ViewObject.Proxy = 0 # This is mandatory unless we code the ViewProvider too.
# App.ActiveDocument.recompute()

# Since Rotate To Fingers creates consistent geometry, we'll use static vert. for now
# Vertices on back face of top key
# 1,2,5,6
#
# Vertices on front face of middle key
# 3,4,12,7

mid = doc.getObject("point_middle")
top = doc.getObject("point_top")

#vertlist = [mid.Shape.Vertexes[4],mid.Shape.Vertexes[12],mid.Shape.Vertexes[7],mid.Shape.Vertexes[3],top.Shape.Vertexes[2],top.Shape.Vertexes[5],top.Shape.Vertexes[6],top.Shape.Vertexes[1]]

# Must refernce by name
vertlist = [mid.getSubObject("Vertex4"),mid.getSubObject("Vertex12"),mid.getSubObject("Vertex7"),mid.getSubObject("Vertex3"),top.getSubObject("Vertex2"),top.getSubObject("Vertex5"),top.getSubObject("Vertex6"),top.getSubObject("Vertex1")]


for v in vertlist:
    myVecList.append(Base.Vector(v.X,v.Y,v.Z))


#   type must be 'Vector' or tuple of three floats, not Part.Vertex
myObj = doc.addObject("Part::FeaturePython", "web_test")
sp.GenerateSolid(myObj, myVecList)
myObj.ViewObject.Proxy = 0 # This is mandatory unless we code the ViewProvider too.
App.ActiveDocument.recompute()

####
# From same reference, if we were working with a selection:
# sel = FreeCADGui.Selection.getSelection()   # Select an object
# for j in enumerate(sel[0].Shape.Edges): would get edges
# Assuming we can enumerate through objects as well, get the Shape, then geo objects
####
#for obj in objs:
#    #App.Console.PrintMessage(obj) # Prints <Part::PartFeature>
#    pts = obj.Shape.Vertexes # Shape.Vertex - not vectors. Mights still work
#    for vtx in pts:
#        #print(vtx.X,",",vtx.Y,",",vtx.Z)    
#        #App.Console.PrintMessage(vtx)
#        
    
    

####
# Generate Web Geo Primatives
# Here we have options. 
# I think the most stable way is probably to either create copies of geometry, then fuse
# or, use points -> create edges -> create a wire -> create a solid -> fuse
# all fuses will probably have to happen LAST. since 
####

"""
