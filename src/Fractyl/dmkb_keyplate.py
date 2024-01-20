# pyright: reportMissingImports=false
import FreeCAD as App
import Part, math

# print(App.Units.Length)

botvec = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
topvec = [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]

# FreeCAD parametric Object version of the Dactly Manuform python port by ashreve

# TEMPORARY CONSTANT VARIABLES
keyswitch_height = 14.0
keyswitch_width = 14.0
plate_style = "UNDERCUT"
sa_profile_key_height = 12.7
sa_length = 18.5
sa_double_length = 37.5
plate_thickness = 4 + 1.1
plate_rim = 1.5 + 0.5

# Undercut style dimensions
clip_thickness = 1.1
clip_undercut = 1.0

mount_width = keyswitch_width + (2 * plate_rim)
mount_height = keyswitch_height + (2 * plate_rim)
mount_thickness = plate_thickness


##############################################
# FREECAD SPECIFIC GEOMETRY GENERATIION
##############################################
def toCenter(w, h, z):
    v = App.Vector(-(w / 2), -(h / 2), -(z / 2))
    return v
  

class ParametricKeyPlate:
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyFloat", "KeyHeight")
        obj.addProperty("App::PropertyFloat", "KeyWidth")
        obj.addProperty("App::PropertyFloat", "PlateThickness")
        obj.addProperty("App::PropertyFloat", "PlateRim")
        obj.addProperty("App::PropertyFloat", "ClipThickness")
        obj.addProperty("App::PropertyFloat", "ClipUndercut")
        obj.addProperty("App::PropertyString", "PlateType")
        
        # Defaults, Hardcodeed for now
        obj.KeyHeight = keyswitch_height
        obj.KeyWidth = keyswitch_width
        obj.PlateThickness = plate_thickness
        obj.PlateRim = plate_rim
        obj.ClipThickness = clip_thickness
        obj.ClipUndercut = clip_undercut
        obj.PlateType = "UNDERCUT"

    def execute(self, obj):
        
        # setup internal geo variabls
        kh = obj.KeyHeight
        kw = obj.KeyWidth
        ph = kh + (2 * obj.PlateRim)
        pw = kw + (2 * obj.PlateRim)
        pt = obj.PlateThickness
        uch = kh + (2 * obj.ClipUndercut)
        ucw = kw + (2 * obj.ClipUndercut)

        """
        keycenter = App.Vector( -( kw / 2 ) , -( kh / 2 ) , -( pt / 2 ) )
        platecenter = App.Vector( -( pw / 2 ) , -( ph / 2 ) , -( pt / 2 ) )
        cutcenter = App.Vector( -( ucw / 2 ) , -( uch / 2 ) , -( pt / 2 ) )
        """

        # make outer dim plate box
        ##############################
        # makeBox(length,width,height,[pnt,dir])
        # Description: Makes a box located at pnt with the dimensions (length,width,height).
        # By default pnt is Vector(0,0,0) and dir is Vector(0,0,1)
        ##############################
        plate = Part.makeBox(pw, ph, pt, toCenter(pw, ph, pt))  # platecenter)

        # make keyhole opening
        keyhole = Part.makeBox(kw, kh, pt, toCenter(kw, kh, pt))

        # make clip undercut geometry
        undercut = Part.makeBox(
            ucw, uch, pt - obj.ClipThickness, toCenter(ucw, uch, pt)
        )

        # add clip geo to keyhole geo
        cutout = keyhole.fuse(undercut)

        # Subtrace kh+clip from plate
        keyplate = plate.cut(cutout)
        
        # Add Placement member to locate / rotate keyplate
        keyplate.Placement = obj.Placement
        
        # Set shape to our new keyplate geometry
        obj.Shape = keyplate

