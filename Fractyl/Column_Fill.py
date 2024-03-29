import FreeCAD as App
import Part
from FreeCAD import Base

keyrows = ['top','middle','bottom']
fingers = ['point', 'index', 'ring', 'pinky']

class ColumnFill:
    """
    Generates a solid given a set of edges.
    Needs some information about which 'corner' 
    of the solid is upper/lower left/right
    """
    def __init__(self, obj, Top_Points, Bottom_Points, Fill_Direction):
        
        obj.Proxy = self
        
        ''' Add properties to the object. '''
        obj.addProperty("App::PropertyVectorList","Top_Points")
        obj.addProperty("App::PropertyVectorList","Bottom_Points")
        obj.addProperty("App::PropertyVector","Fill_Direction")
        
        obj.Top_Points = Top_Points
        obj.Bottom_Points = Bottom_Points
        obj.Fill_Direction = Fill_Direction
        #obj.PlateType = ""
    
    def execute(self, fp):
            # Create extruded surfaces from two wires
            # Fill remaining side faces
            # enclose as Solid
            Top_Points = fp.Top_Points
            Bottom_Points = fp.Bottom_Points
            
            top_edge_list = []
            bottom_edge_list = []
            App.Console.PrintMessage("Top Edge Creation:\n")
            for i in range(0,len(Top_Points)-1,2):
                edge = Part.LineSegment(Top_Points[i],Top_Points[i+1]).toShape()
                top_edge_list.append(edge)
                App.Console.PrintMessage(f"Edge #{i} is : {edge}\n")
            
            App.Console.PrintMessage("Bottom Edge Creation:\n")
            for i in range(0,len(Bottom_Points)-1,2):
                edge = Part.LineSegment(Bottom_Points[i],Bottom_Points[i+1]).toShape()
                bottom_edge_list.append(edge)
                App.Console.PrintMessage(f"Edge #{i} is : {edge}\n")
                
            top_wire = Part.Wire(top_edge_list)
            bottom_wire = Part.Wire(bottom_edge_list)

            # Get first and last edges to find endpoints
            # Necessary because points aren't guaranteed in order
            # Due to geometry orientation
            first_top = top_edge_list[0]
            last_top =  top_edge_list[-1]
            
            first_bot = bottom_edge_list[0]
            last_bot = bottom_edge_list[-1]
            
            # Get Start and End Points
            start_top = first_top.Vertexes[0] if first_top.Vertexes[0].Y > first_top.Vertexes[1].Y else first_top.Vertexes[1]
            end_top = last_top.Vertexes[0] if last_top.Vertexes[0].Y > last_top.Vertexes[1].Y else last_top.Vertexes[1]
            
            start_bot = first_bot.Vertexes[0] if first_bot.Vertexes[0].Y > first_bot.Vertexes[1].Y else first_bot.Vertexes[1]
            end_bot = last_bot.Vertexes[0] if last_bot.Vertexes[0].Y > last_bot.Vertexes[1].Y else last_bot.Vertexes[1]
            
            # Get starting diagonal vector
            start_sep_vec = start_bot.Point.sub(start_top.Point) # might be opposite direction i need...
            
            # component of sep in fill dir
            # Apologies to my Linear Algebra professor
            # We could just assume we are always working extruding in X, but
            # we have a vector direction, so componentwise multiply
            ext_vec = start_sep_vec.scale(fp.Fill_Direction.x, fp.Fill_Direction.y,fp.Fill_Direction.z ) 
            # top gets positive extrude, bottom gets negative extrude
                        
            # Extrude wires
            top_face = top_wire.extrude(ext_vec)
            #bottom_face = bottom_wire.extrude(ext_vec.negative())

            # Connect top and bottom edges with additional wires to form a closed shape
            # ... Code to connect edges ...

            # Check if the shape is watertight
            # ... Code to check if watertight ...

            # Create a solid from the shape
            # ... Code to create a solid ...
            
            # Update the feature
            fp.Shape = top_face  # Set the final shape


# Function to comprehend column structure and run geometry generators
# Refactored out of columnfill class.
def fillColumns(Column_Name_List):
    doc = App.activeDocument()
    objects = doc.Objects
    
    plate_objects = [obj for obj in objects if hasattr(obj, 'PlateType')]
    
    for plt in plate_objects:
        App.Console.PrintMessage(f"Plate Objects Found:\n{plt.Label}\n")
    
    column_list = Column_Name_List # Was a class member of ColumnFill...
    
    # Define the table as a dictionary for easy lookup
    edge_table = {
        ('UNDERCUT','Upper','Right'): 'Edge9',
        ('UNDERCUT','Upper', 'Left'): 'Edge2',
        ('UNDERCUT','Lower','Right'): 'Edge16',
        ('UNDERCUT','Lower', 'Left'): 'Edge4',
        ('WEB','Upper','Right'):'Edge8',
        ('WEB','Upper', 'Left'):'Edge1',
        ('WEB','Lower','Right'):'Edge5',
        ('WEB','Lower', 'Left'):'Edge7'
    }

    # Process pairs of columns
    for i in range(0, len(column_list) - 1, 2):
        App.Console.PrintMessage(f"Currently getting column {i} and {i+1}\n")
        column1 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i]]
        column2 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i + 1]]

        # Sort objects based on Y coordinate (was Z - Y better for actual key column)
        column1.sort(key=lambda obj: obj.Placement.Base.y)
        column2.sort(key=lambda obj: obj.Placement.Base.y)
        
        # Determine which column is in fact higher in Z coords
        top_col = column1 if column1[0].Placement.Base.z > column2[0].Placement.Base.z else column2
        bottom_col = column1 if column1[0].Placement.Base.z < column2[0].Placement.Base.z else column2
        
        # Technically, we know which order our columns come in as, but checking x 
        # Coordingates for side determination because why not add bugs. . .
        if top_col[0].Placement.Base.x < bottom_col[0].Placement.Base.x :
            high_edge = 'Right' 
            low_edge = 'Left'
        else:
            high_edge = 'Left' 
            low_edge = 'Right'
        
        top_edge_names = []
        bottom_edge_names = []
        for plt in top_col:
            top_edge_names.append(edge_table[(plt.PlateType, 'Upper', high_edge)])
        
        for plt in bottom_col:
            bottom_edge_names.append(edge_table[(plt.PlateType, 'Lower', low_edge)])
        
        # generate a list of Edge objects
        top_edge_list = []
        bottom_edge_list = []
        for j, plt in enumerate(top_col):
            edge = plt.getSubObject(top_edge_names[j])
            top_edge_list.append(edge.Vertexes[0].Point)
            top_edge_list.append(edge.Vertexes[1].Point)
            
        for j, plt in enumerate(bottom_col):
            edge = plt.getSubObject(bottom_edge_names[j])
            bottom_edge_list.append(edge.Vertexes[0].Point)
            bottom_edge_list.append(edge.Vertexes[1].Point)
        
        
        App.Console.PrintMessage(f"Top Edges\n{top_edge_list}\n")
        App.Console.PrintMessage(f"Bottom Edges\n{bottom_edge_list}\n")
        
        
        obj = doc.addObject("Part::FeaturePython", "ColumnFill") # just create generic object I think
        # Note: Surfaces need to extrude in X
        ColumnFill(obj, top_edge_list, bottom_edge_list, Base.Vector(1,0,0))
        doc.recompute()
    
    return None

# Add feature to the document
if __name__ == '__main__':
    #makeColumnFill()
    fillColumns(fingers)
