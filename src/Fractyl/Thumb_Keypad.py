# Generate Thumb Button Pad

from .Rotate_To_Fingers import create_transformation, makeKey
import FreeCAD as App
import math
from FreeCAD import Base
####
# We need to create buttons for the thumb.
# In MediaPipe parlance, We've assumed our origin at the Index Finger MCP
# we would need to Subtract / travers back to the wrist joint, then to the thumb MCP
# The thumb doesn't quite rotate from the CMC.
# We would want buttons some reasonable angle offset at the distance
# between point 2 (thumb MCP) and point 4 (thumb tip).
# My thumb MCP-CMC axis is about 40-45 degrees  offste from IF MCP-T CMC axis,
# ~40 mm between MCP and CMC, and about 55-60 mm from MCP to tip
# With those datums, about 30 deg inboard and 45 deg outboard are reasonable angle excursions
# ~ 70 mm from IF MCP to T CMC
####

# Create a translate / rotate chain to neutral position
# origin -> -70 Y | 40mm at 40 degrees = Thumb MCP 
# Thumb MCP -> 55 mm (at 40 deg, or along Thumb Neutral vector)
def create_thumbpad():
    mcpif_cmct_dist = 50 #mm
    tmc_angle = 40 #deg
    tcmc_mcp_dist = 45
    t_length = 55.0
    thumb_cmc_pos = Base.Vector(0,-mcpif_cmct_dist,0)
    thumb_cmc_rot = Base.Rotation(-30,-20,0)
    thumb_cmc_pmat =  App.Placement()
    thumb_cmc_pmat.Base = thumb_cmc_rot.multVec(thumb_cmc_pos)

    thumb_mcp_pos = Base.Vector(0,tcmc_mcp_dist,0)
    thumb_mcp_rot =  Base.Rotation(Base.Vector(0, 0, 1), tmc_angle)
    thumb_mcp_pmat = App.Placement()
    thumb_mcp_pmat.Rotation = thumb_mcp_rot
    thumb_mcp_pmat.Base = thumb_mcp_rot.multVec(thumb_mcp_pos)
    
    thumb_mcp_pmat = thumb_mcp_pmat.multiply(thumb_cmc_pmat)

    # 20 mm button seperation is sufficient
    # so 20 / t_length = sin(theta)
    offset_angle = math.degrees( math.asin(20/t_length) ) # 21.3 - ok if it's 22 degrees
    #offset_angle = 30
    num_btns = 3
    btn_names = ['inside','middle','outside']
    btn_row_order = [-1,0,1]
    btn_col_order = [1] # probably not needed right now, but for future expansion
    thumb = dict(zip(btn_names,btn_row_order))
    finger_name = 'thumb'

    xform = App.Placement()

    for btn in thumb:
        # set initial displacement to thumb origin
        place = App.Placement()
        place = thumb_cmc_pmat
        
        # transform to mcp
        place = place.multiply(thumb_mcp_pmat) # Should be affine translation + rotation to thumb MCP joint

        # Calculate Button Rotation. Neutral angle = tmc angle
        btn_angle = tmc_angle + ( thumb[btn] * offset_angle)
        btn_rot = Base.Rotation(Base.Vector(0, 0, 1), btn_angle)

        # Calculate Button Offset Vector
        btn_vec = btn_rot.multVec(Base.Vector(0,t_length,0))
        
        # Create Transform matrix
        xform.Base = btn_vec
        xform.Rotation = btn_rot

        # Transform btn placement to final position/orientation
        place = place.multiply(xform)

        # Create keyplate body
        obj = makeKey(name = 'thumb_'+btn)
        obj.Placement = place

        App.ActiveDocument.recompute()
        App.Console.PrintMessage(f"created {btn} thumb button\n")
    #
    
if __name__ == "__main__":
    App.Console.PrintMessage("Creating thumb buttons from 'main'\n")
    create_thumbpad()



        




