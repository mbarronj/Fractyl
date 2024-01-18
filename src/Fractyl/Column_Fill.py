import FreeCAD, FreeCADGui
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
    def __init__(self, obj, columns):
        
        obj.Proxy = self
        
        ''' Add properties to the object. '''
        #obj.addProperty("App::PropertyString","PlateType")
        obj.addProperty("App::PropertyStringList","Column_Names")
        
        obj.Column_Names = columns
        #obj.PlateType = ""
        
        

    def execute(self, fp):
        doc = FreeCAD.activeDocument()
        objects = doc.Objects
        plate_objects = [obj for obj in objects if hasattr(obj, 'PlateType')]
        
        for plt in plate_objects:
            FreeCAD.Console.PrintMessage(f"Plate object label : {plt.Label}\n")
        
        column_list = fp.Column_Names
        
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
            FreeCAD.Console.PrintMessage(f"Currently getting column {i} and {i+1}\n")
            column1 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i]]
            column2 = [obj for obj in plate_objects if obj.Label.split('_')[0] == column_list[i + 1]]

            # Sort objects based on Y coordinate (was Z - Y better for actual column)
            column1.sort(key=lambda obj: obj.Placement.Base.y)
            column2.sort(key=lambda obj: obj.Placement.Base.y)
            
            #FreeCAD.Console.PrintMessage(f"Column of objects 1: {column1}\n\n")
            
            #FreeCAD.Console.PrintMessage(f"Column of objects 2: {column2}\n\n")

            # Get the top object from the highest column and bottom object from the lowest column
            #top_obj = column1[-1] if column1[-1].Placement.Base.z > column2[-1].Placement.Base.z else column2[-1]
            #bottom_obj = column1[0] if column1[0].Placement.Base.z < column2[0].Placement.Base.z else column2[0]
            
            top_col = column1 if column1[0].Placement.Base.z > column2[0].Placement.Base.z else column2
            bottom_col = column1 if column1[0].Placement.Base.z < column2[0].Placement.Base.z else column2
            
            if top_col[0].Placement.Base.y < bottom_col[0].Placement.Base.y :
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
            
            # Extract edges and create wires
            #top_edge_name = edge_table[(top_obj.PlateType, 'Upper', 'Right' if i % 4 == 0 else 'Left')]
            #bottom_edge_name = edge_table[(bottom_obj.PlateType, 'Lower', 'Right' if i % 4 == 2 else 'Left')]
            
            top_edge_list = []
            bottom_edge_list = []
            for j, plt in enumerate(top_col):
                top_edge_list.append(getattr(plt.Shape, top_edge_names[j]))
                
            for j, plt in enumerate(bottom_col):
                bottom_edge_list.append(getattr(plt.Shape, bottom_edge_names[j]))

            top_wire = Part.Wire(top_edge_list)
            bottom_wire = Part.Wire(bottom_edge_list)

            # Extrude wires
            side_vectors = {'Right':Base.Vector(2, 0, 0) ,'Left':Base.Vector(-2, 0, 0)   }
            # Base.Vector(2, 0, 0)  # X separation of 2mm
            
            top_face = top_wire.extrude(side_vector[high_edge])
            bottom_face = bottom_wire.extrude(side_vector[low_edge])

            # Connect top and bottom edges with additional wires to form a closed shape
            # ... Code to connect edges ...

            # Check if the shape is watertight
            # ... Code to check if watertight ...

            # Create a solid from the shape
            # ... Code to create a solid ...

        # Update the feature
        fp.Shape = top_face  # Set the final shape

# Function to add feature to the document
def makeColumnFill():
    doc = FreeCAD.activeDocument()
    if doc is None:
        doc = FreeCAD.newDocument()
    obj = doc.addObject("Part::FeaturePython", "ColumnFill",fingers)
    ColumnFill(obj, fingers)
    doc.recompute()
    return obj

# Function to comprehend column structure and run geometry generators
# Refactored out of columnfill class.
def fillColumns(Column_Name_List):
    doc = FreeCAD.activeDocument()
    objects = doc.Objects
    
    plate_objects = [obj for obj in objects if hasattr(obj, 'PlateType')]
    
    for plt in plate_objects:
        FreeCAD.Console.PrintMessage(f"Plate Objects Found:\n{plt.Label}\n")
    
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
        FreeCAD.Console.PrintMessage(f"Currently getting column {i} and {i+1}\n")
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
            top_edge_list.append(getattr(plt.Shape, top_edge_names[j]))
            
        for j, plt in enumerate(bottom_col):
            bottom_edge_list.append(getattr(plt.Shape, bottom_edge_names[j]))
        
        obj = doc.addObject("Part::FeaturePython", "ColumnFill") # ,fingers) just create generic object I think
        ColumnFill(obj, top_edge_list, bottom_edge_list)
        doc.recompute()
    
    return None

# Add feature to the document
if __name__ == '__main__':
    makeColumnFill()
