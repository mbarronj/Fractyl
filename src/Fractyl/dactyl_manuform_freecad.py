# pyright: reportMissingImports=false
import FreeCAD as App
import Part, math

# print(App.Units.Length)

botvec = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
topvec = [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]

# FreeCAD parametric Object version of the Dactly Manuform python port by ashreve
"""
###############################################
# COPIED: EXTREMELY UGLY BUT FUNCTIONAL BOOTSTRAP
###############################################

## IMPORT DEFAULT CONFIG IN CASE NEW PARAMETERS EXIST
import generate_configuration as cfg
for item in cfg.shape_config:
    locals()[item] = cfg.shape_config[item]

if len(sys.argv) <= 1:
    print("NO CONFIGURATION SPECIFIED, USING run_config.json")
    with open(os.path.join(r".", 'run_config.json'), mode='r') as fid:
        data = json.load(fid)

else:
    ## CHECK FOR CONFIG FILE AND WRITE TO ANY VARIABLES IN FILE.
    opts, args = getopt.getopt(sys.argv[1:], "", ["config="])
    for opt, arg in opts:
        if opt in ('--config'):
            with open(os.path.join(r"..", "configs", arg + '.json'), mode='r') as fid:
                data = json.load(fid)

for item in data:
    locals()[item] = data[item]
"""
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
undercut_transition = 0.2  # NOT FUNCTIONAL WITH OPENSCAD, ONLY WORKS WITH CADQUERY

# Custom plate step file
plate_file = None
plate_offset = 0.0

mount_width = keyswitch_width + (2 * plate_rim)
mount_height = keyswitch_height + (2 * plate_rim)
mount_thickness = plate_thickness

"""
# Derived values
if plate_style in ['NUB', 'HS_NUB']:
    keyswitch_height = nub_keyswitch_height
    keyswitch_width = nub_keyswitch_width
elif plate_style in ['UNDERCUT', 'HS_UNDERCUT', 'NOTCH', 'HS_NOTCH']:
    keyswitch_height = undercut_keyswitch_height
    keyswitch_width = undercut_keyswitch_width
else:
    keyswitch_height = hole_keyswitch_height
    keyswitch_width = hole_keyswitch_width

if 'HS_' in plate_style:
    symmetry = "asymmetric"
    plate_file = path.join(parts_path, r"hot_swap_plate")
    plate_offset = 0.0
    
if nrows > 5:
    column_style = column_style_gt5

centerrow = nrows - centerrow_offset
lastrow = nrows - 1

if reduced_outer_cols>0 or reduced_inner_cols>0:
    cornerrow = lastrow - 1
else:
    cornerrow = lastrow
lastcol = ncols - 1
"""


##############################################
# FREECAD SPECIFIC GEOMETRY GENERATIION
##############################################
def toCenter(w, h, z):
    v = App.Vector(-(w / 2), -(h / 2), -(z / 2))
    return v

#def genCurve():
    

class ParametricKeyPlate:
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyFloat", "KeyHeight")
        obj.addProperty("App::PropertyFloat", "KeyWidth")
        obj.addProperty("App::PropertyFloat", "PlateThickness")
        obj.addProperty("App::PropertyFloat", "PlateRim")
        obj.addProperty("App::PropertyFloat", "ClipThickness")
        obj.addProperty("App::PropertyFloat", "ClipUndercut")
        
        # Defaults, Hardcodeed for now
        obj.KeyHeight = keyswitch_height
        obj.KeyWidth = keyswitch_width
        obj.PlateThickness = plate_thickness
        obj.PlateRim = plate_rim
        obj.ClipThickness = clip_thickness
        obj.ClipUndercut = clip_undercut

    def execute(self, obj):
        # re-importing FreeCAD?

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
        # box.Placement = obj.Placement
        keyplate.Placement = obj.Placement
        # obj.Shape = box
        obj.Shape = keyplate


myObj = App.ActiveDocument.addObject("Part::FeaturePython", "Key_Plate")
ParametricKeyPlate(myObj)
myObj.ViewObject.Proxy = 0  # This is mandatory unless we code the ViewProvider too.
App.ActiveDocument.recompute()
