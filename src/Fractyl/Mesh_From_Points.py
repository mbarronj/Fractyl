# pyright: reportMissingImports=false
import FreeCAD as App
import Part
import Mesh
from FreeCAD import Base
import math
from .Solid_From_Points import GenerateSolid

####
# Generates a shape from a list of points
# Assumes points are in the configuration generated
# by the Fractyl Rotate_to_fingers and Create_Web modules
# Reference:
# https://wiki.freecad.org/Part_ShapeFromMesh
#
#pth = "C:\\Users\\mbarr\\OneDrive\\Documents\\01. Projects\\03_SW_Dev\\Fractyl\\src\\Fractyl"
#filename = "Mesh_From_Points.py"
#exec(open(pth + "\\" + filename).read())


# Define the table as a dictionary for easy lookup
edge_table = {
    ('UNDERCUT','Upper','Right'): 'Edge9',
    ('UNDERCUT','Upper', 'Left'): 'Edge2',
    ('UNDERCUT','Lower','Right'): 'Edge16',
    ('UNDERCUT','Lower', 'Left'): 'Edge4',
    ('WEB','Upper','Right'):'Edge8',
    ('WEB','Upper', 'Left'):'Edge10',
    ('WEB','Lower','Right'):'Edge5',
    ('WEB','Lower', 'Left'):'Edge7'
}

keyrows = ['top','middle','bottom']
fingers = ['point', 'index', 'ring', 'pinky']

def addPiping(pts_list,radius = 1, pipname = 'pip_'):
    """Adds small cylinders intended to allow easier fuse/union by OCC"""
    if len(pts_list) == 2:
        start_pt = pts_list[0]
        end_pt = pts_list[1]
        # probably smart to check both, but man that's a lot of work...sigh
        if isinstance(start_pt, Base.Vector) and isinstance(end_pt, Base.Vector): 
            cyl_vec = start_pt.sub(end_pt)
            vert = Base.Vector(0,0,1)
            # Vector Magic
            angle = math.degrees(vert.getAngle(cyl_vec)) # vector angle in rad
            length = end_pt.distanceToPoint(start_pt)
            rotvec = Base.Vector(1,0,0) #start_pt.cross(end_pt) #cross product is unneeded
            
            # Create rotation
            rotation = Base.Rotation(rotvec, -(angle + 180)) # rotation needs degrees, quadrant correction

            # Create translation
            translation = start_pt

            # Combine translation and rotation into a transformation matrix
            place = App.Placement()
            place.Base = translation
            place.Rotation = rotation   

            # Now Create Geometry
            doc = App.activeDocument()

            cylinder = doc.addObject("Part::Cylinder", pipname)
            cylinder.Radius = radius
            cylinder.Height = length
            cylinder.Placement = place

            doc.recompute()
            return cylinder
        else:
            App.Console.PrintMessage(f"either {start_pt} or {end_pt} were not actually {type(Base.Vector)}\n")
            return None
    else:
         App.Console.PrintMessage(f"{len(pts_list)} was not equal to 2\n")
         return None



def eliminateDupes(pts):
    """Examines X,Y,Z, coordinates of FC Points/vectors to determine similarity """
    eps = 0.1 # error term. 0.1 mm is large, but I think good enough for 3D printing
    # sort by Y for keyboard purposes, then eliminate neighbors
    pts.sort(key=lambda pt: pt.y, reverse=True)
    App.Console.PrintMessage(f"Sorted points:\n{pts}\n")
    unique_pts = [pts[0]]
    numpts = len(pts)
    samept = lambda cur, prev: abs(cur.distanceToPoint(prev)) <= eps
    # unique_pts.extend(filter(samept,pts[1:numpts]))
    
    #check if current point is same as last point
    for i in range(1,numpts):

        if not samept(pts[i], pts[i-1]):
            unique_pts.append(pts[i])
       
    App.Console.PrintMessage(f"Sorted unique points:\n{unique_pts}\n")
    return unique_pts


class MeshFromPoints():
    """
    Generates a mesh given a set of vector coordinates
    """
    def __init__(self, obj, Points):
        
        obj.Proxy = self
        
        ''' Add properties to the object. '''
        obj.addProperty("App::PropertyVectorList","Points")
       
        obj.Points = Points
  
    def execute(self, obj):
        # Create extruded surfaces from two wires
        # Fill remaining side faces
        # enclose as Solid
        v = obj.Points
        
        # eliminate duplicate points, sort for later

        d = Mesh.polynomialFit(v)
        c = d["Coefficients"]
        App.Console.PrintMessage("Polynomial: f(x,y)=%f*x^2%+f*y^2%+f*x*y%+f*x%+f*y%+f" % (c[0],c[1],c[2],c[3],c[4],c[5]))
        #for i in d["Residuals"]:
        #    self.assertTrue(math.fabs(i) < 0.0001, "Too high residual %f" % math.fabs(i))

        # Set placement and featurePython shape
        d.Placement = obj.Placement
        obj.Shape = d

# Function to comprehend column structure and run geometry generators
# Refactored out of columnfill class.
def fillColumnMesh(Column_Name_List):
    doc = App.activeDocument()
    objects = doc.Objects
    
    plate_objects = [obj for obj in objects if hasattr(obj, 'PlateType')]
    
    for plt in plate_objects:
        App.Console.PrintMessage(f"Plate Objects Found:\n{plt.Label}\n")
    
    column_list = Column_Name_List # Was a class member of ColumnFill...
    
    # Process pairs of columns
    for i in range(0, len(column_list) - 1):
        App.Console.PrintMessage(f"Currently getting column {i} and {i+1}\n")
        cname = column_list[i]
        column1 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i]]
        column2 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i + 1]]

        # Sort objects based on Y coordinate (was Z - Y better for actual key column)
        column1.sort(key=lambda obj: obj.Placement.Base.y)
        column2.sort(key=lambda obj: obj.Placement.Base.y)
        
        # All that I really need are left and right points, the facing sides. 
        # Those can come from the edges
        leftcol_top_names = []
        leftcol_bot_names = []
        rightcol_top_names = []
        rightcol_bot_names = []
        for plt in column1:
            leftcol_top_names.append(edge_table[(plt.PlateType, 'Upper', 'Right')])
            leftcol_bot_names.append(edge_table[(plt.PlateType, 'Lower', 'Right')])
        
        for plt in column2:
            rightcol_top_names.append(edge_table[(plt.PlateType, 'Upper', 'Left')])
            rightcol_bot_names.append(edge_table[(plt.PlateType, 'Lower', 'Left')])
        
        # generate a list of Edge objects
        # Yeah, I know this could be done more elegantly
        # But would you then be able to understand what's happening Geometrically?
        tl_pts = []
        bl_pts = []
        tr_pts = []
        br_pts = []
        for j, plt in enumerate(column1):
            t_edge = plt.getSubObject(leftcol_top_names[j])
            b_edge = plt.getSubObject(leftcol_bot_names[j])
            tl_pts.append(t_edge.Vertexes[0].Point)
            tl_pts.append(t_edge.Vertexes[1].Point)
            bl_pts.append(b_edge.Vertexes[0].Point)
            bl_pts.append(b_edge.Vertexes[1].Point)
            
        for j, plt in enumerate(column2):
            t_edge = plt.getSubObject(rightcol_top_names[j])
            b_edge = plt.getSubObject(rightcol_bot_names[j])
            tr_pts.append(t_edge.Vertexes[0].Point)
            tr_pts.append(t_edge.Vertexes[1].Point)
            br_pts.append(b_edge.Vertexes[0].Point)
            br_pts.append(b_edge.Vertexes[1].Point)

        # Clean / Concatenate those points
        tl_pts = eliminateDupes(tl_pts)
        bl_pts = eliminateDupes(bl_pts)
        tr_pts = eliminateDupes(tr_pts)
        br_pts = eliminateDupes(br_pts)
        
        # Loop over points by pairs, create 4-sided solid
        for k in range(len(tl_pts)-1):
            # taking sides of each column as the "top" or "bottom"
            # Have to remember that points need to run in RH order
            myVecList = [ tl_pts[k],tl_pts[k+1],bl_pts[k+1],bl_pts[k],tr_pts[k],tr_pts[k+1],br_pts[k+1],br_pts[k]]
            myObj = doc.addObject("Part::FeaturePython", cname+"_columnfill_solid_"+str(k))
            GenerateSolid(myObj, myVecList)
            myObj.ViewObject.Proxy = 0 # not coding viewprovider
            doc.recompute()


        ####
        # Mesh Generation - problematic and complicated.
        # Switching to generating solids with the now-cleanly arranged points
        ####

        # # Mesh Generic
        # mesh = Mesh.Mesh() # Creates a generic mesh object to manipulate
        # # Add Facet takes 3 vectors as input
        # # Assuming equal numbers of points, arranged in order, no dupes
        # # Top surfaces
        # for i in range(1,len(tl_pts)):
        #     mesh.addFacet(tl_pts[i-1],tl_pts[i],tr_pts[i-1]) # first corner
        #     mesh.addFacet(tl_pts[i],tr_pts[i],tr_pts[i-1]) # second corner
        # # bottom surfaces
        # for i in range(1,len(bl_pts)):
        #     mesh.addFacet(bl_pts[i-1],bl_pts[i],br_pts[i-1]) # first corner
        #     mesh.addFacet(bl_pts[i],br_pts[i],br_pts[i-1]) # second corner
        # # Left Surface
        # for i in range(1,len(bl_pts)):
        #     mesh.addFacet(tl_pts[i-1],tl_pts[i],bl_pts[i-1]) # first corner
        #     mesh.addFacet(bl_pts[i-1],bl_pts[i],tl_pts[i]) # second corner
        # # Right Surface
        # for i in range(1,len(bl_pts)):
        #     mesh.addFacet(tr_pts[i-1],tr_pts[i],br_pts[i-1]) # first corner
        #     mesh.addFacet(br_pts[i-1],br_pts[i],tr_pts[i]) # second corner
        # # front surface
        # mesh.addFacet(tl_pts[0],bl_pts[0],tr_pts[0]) # first corner
        # mesh.addFacet(tr_pts[0],br_pts[0],bl_pts[0]) # second corner
        # # rear surface
        # mesh.addFacet(tl_pts[-1],bl_pts[-1],tr_pts[-1]) # first corner
        # mesh.addFacet(tr_pts[-1],br_pts[-1],bl_pts[-1]) # second corner
        
        # # Make and Refine Mesh Object
        # App.Console.PrintMessage(f"\nColumn Index is: {i}\n")
        # meshObj = doc.addObject("Mesh::Feature", "MeshFill")
        # meshObj.Mesh = mesh
        # meshObj.fixIndices()
        # meshObj.harmonizeNormals()
        
        # # Print the label 
        # App.Console.PrintMessage(f"\nMesh Object info: {meshObj.Label}\n")
        # # Make solid object
        # solidObj = doc.addObject('Part::Feature', f"ColumnFill_{i}")
        # tempshape = Part.Shape()
        # tempshape.makeShapeFromMesh(meshObj.Mesh.Topology, 0.050000, False)
        # solidObj.Shape = tempshape
        # solidObj.purgeTouched() # No clue why this is needed, but it's critical
        # # Still Actually not a solid shape, just a shell
        # # Solidify shell into solid part
        # __s__=solidObj.Shape.Faces
        # __s__=Part.Solid(Part.Shell(__s__))
        # __o__=doc.addObject("Part::Feature",f"{cname}_ColumnFill_solid_{i}")
        # __o__.Shape=__s__
        # #Part.show(__o__)
        # __o__.purgeTouched() # maybe important here too?
        # # Hide surf and mesh
        # solidObj.Visibility = False
        # meshObj.Visibility = False
        # App.Console.PrintMessage(f"\nFinished with column fill: {__o__.Label}\n")
        doc.recompute()

        # Add piping for later fuse ops
        # points should already be sorted
        for idx in range(len(bl_pts)-1):
            pipe = addPiping([bl_pts[idx],bl_pts[idx+1]],radius=1,pipname=cname+"_pip_") # radius = 1 by default
            pipe = addPiping([br_pts[idx],br_pts[idx+1]],radius=1,pipname=cname+"_pip_")
            if pipe is not None:
                App.Console.PrintMessage("added pipe\n")
            else:
                App.Console.PrintMessage(f"Error adding pipe:{[bl_pts[idx],bl_pts[idx+1]]} ")
        
        # Recompute one last time
        doc.recompute()
        
    return None
    
if __name__ == "__main__":
    """
    Run generation function for test purposes
    """
    App.Console.PrintMessage(f"\nMesh_From_Points running as Main\nGenerating a Mesh object from:\n {fingers}\n")
    fillColumnMesh(fingers)
   

        