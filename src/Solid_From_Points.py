import FreeCAD
import Part, math

# print(FreeCAD.Units.Length)

#botvec = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
#topvec = [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]



class GeneratedSolid(topvec,botvec):
	def __init__(self, obj):
		obj.Proxy = self
		#obj.addProperty("App::PropertyFloat", "Length")
		#obj.addProperty("App::PropertyFloat", "Width")
		#obj.addProperty("App::PropertyFloat", "Height")
	
	def execute(self, obj):
		#re-importing FreeCAD?
		import FreeCAD
		import Part
		
		L = obj.Length
		W = obj.Width
		H = obj.Height
		
		L = 5.0
		W = 4.0
		H = 3.0
		

		prms =  (L, W, H) # tuple - not updateable
		for p in prms:
			if( p == 0): # cheeky attempt at user input sanitation
				print("Dimension Cannot Be Zero")
				return
		
		# Create vertices
		vertices = []		
		for v in botvec:
			vi = FreeCAD.Vector( prms[0]*v[0], prms[1]*v[1], prms[2]*v[2])
			vertices.append(vi)
		
		for v in topvec:
			vi = FreeCAD.Vector( prms[0]*v[0], prms[1]*v[1], prms[2]*v[2])
			vertices.append(vi)
		
		# Create Edges
		bottomEdges = []
		for i in range(4):
			edge = Part.LineSegment(vertices[i] , vertices[ (i+1)%4 ]).toShape()
			bottomEdges.append(edge)
			
		topEdges = []
		for i in range(4):
			edge = Part.LineSegment(vertices[i+4] , vertices[ ((i+1)%4) + 4 ]).toShape()
			topEdges.append(edge)
		
		vertEdges = []
		for i in range(4):
			edge = Part.LineSegment(vertices[i] , vertices[ (i+4) ]).toShape()
			vertEdges.append(edge)
		
		# Create Wires (TODO: Add check for closure)
		bottomWire = Part.Wire(bottomEdges)
		topWire = Part.Wire(topEdges)
		
		# Create Side Face Wires
		side1 = Part.Wire( [ bottomEdges[0], vertEdges[1], topEdges[0], vertEdges[0]] ) 		
		side2 = Part.Wire( [ bottomEdges[1], vertEdges[2], topEdges[0], vertEdges[1]] ) 		
		side3 = Part.Wire( [ bottomEdges[2], vertEdges[3], topEdges[2], vertEdges[2]] )
		side4 = Part.Wire( [ bottomEdges[3], vertEdges[0], topEdges[3], vertEdges[3]] )

		# Create Top and Bottom Face
		bottom = Part.Face(bottomWire)
		top = Part.Face(topWire)
		front = Part.Face(side1)
		right = Part.Face(side2)
		back = Part.Face(side3)
		left = Part.Face(side4)

		# Create a Solid Box from Faces
		box = Part.Shell( [bottom, front, right, back, left, top] ) 
		#box = Part.Shell( [bottom, front, right,  top] ) 
		
		solidBox = Part.Solid(box)
		# Add object placement, allows movement by user
		#box.Placement = obj.Placement
		solidBox.Placement = obj.Placement

			
		#obj.Shape = box
		obj.Shape = solidBox


myObj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Box")
ParametricCube(myObj)
myObj.ViewObject.Proxy = 0 # This is mandatory unless we code the ViewProvider too.
FreeCAD.ActiveDocument.recompute()
		