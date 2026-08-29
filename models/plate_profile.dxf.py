"""Standalone 2D drawing: plate profile reproduced from the dimensioned sketch (mm).

The sketch over-constrains the profile: the 144 deg / 140 deg chamfer angles do
not close against the linear dimension chain (23+6+10+10 = 8+41 = 49 wide).
The profile is therefore built from the linear dimensions plus the 41 deg
bottom-left chamfer; the two chamfer angle dimensions are reproduced as
labelled annotations from the source sketch.
"""

from __future__ import annotations

import math

import ezdxf

# Named dimension parameters (millimetres), taken from the source sketch.
TOP_LEFT_W = 23.0        # top edge left of the slot
SLOT_W = 6.0             # slot width
SLOT_DEPTH = 14.0        # slot depth below the top edge
CHAMFER_W1 = 10.0        # top edge between slot and chamfer start
CHAMFER_W2 = 10.0        # top edge between chamfer start and right corner
LEFT_H = 28.0            # left vertical edge
BOTTOM_W = 41.0          # bottom edge
RIGHT_H = 34.0           # right vertical edge above the notch
NOTCH_W = 4.0            # bottom-right notch width
NOTCH_H = 6.0            # bottom-right notch height
CHAMFER_ANGLE_DEG = 41.0  # bottom-left chamfer, measured from the vertical

# Derived geometry.
TOTAL_W = TOP_LEFT_W + SLOT_W + CHAMFER_W1 + CHAMFER_W2          # 49
CHAMFER_RUN = TOTAL_W - BOTTOM_W                                 # 8 horizontal
CHAMFER_RISE = CHAMFER_RUN / math.tan(math.radians(CHAMFER_ANGLE_DEG))
TOP_Y = LEFT_H + CHAMFER_RISE
SLOT_BOT_Y = TOP_Y - SLOT_DEPTH
CHAMFER_TOP_Y = RIGHT_H                                          # 34

# Closed profile, counter-clockwise from the top-left corner.
P_TL = (0.0, TOP_Y)
P_SLOT_L = (TOP_LEFT_W, TOP_Y)
P_SLOT_BL = (TOP_LEFT_W, SLOT_BOT_Y)
P_SLOT_BR = (TOP_LEFT_W + SLOT_W, SLOT_BOT_Y)
P_CHAMFER_R = (TOP_LEFT_W + SLOT_W + CHAMFER_W1, CHAMFER_TOP_Y)
P_TR = (TOTAL_W, CHAMFER_TOP_Y)
P_NOTCH_TR = (TOTAL_W, NOTCH_H)
P_NOTCH_M = (TOTAL_W - NOTCH_W, NOTCH_H)
P_NOTCH_B = (TOTAL_W - NOTCH_W, 0.0)
P_BL = (CHAMFER_RUN, 0.0)
P_CHAMFER_L = (0.0, CHAMFER_RISE)
PROFILE = [
    P_TL, P_SLOT_L, P_SLOT_BL, P_SLOT_BR, P_CHAMFER_R, P_TR,
    P_NOTCH_TR, P_NOTCH_M, P_NOTCH_B, P_BL, P_CHAMFER_L,
]


def gen_dxf():
    document = ezdxf.new("R2010")
    document.units = ezdxf.units.MM
    modelspace = document.modelspace()
    document.layers.add("CUT")
    document.layers.add("DIM")
    dim_kwargs = {"dxfattribs": {"layer": "DIM"}, "override": {"dimdec": 0, "dimadec": 0}}

    modelspace.add_lwpolyline(PROFILE, close=True, dxfattribs={"layer": "CUT"})

    # Top linear dimensions on a shared dimension line.
    top_dim_y = TOP_Y + 6
    for p1, p2 in (
        ((0, TOP_Y), (TOP_LEFT_W, TOP_Y)),
        (P_SLOT_L, (TOP_LEFT_W + SLOT_W, TOP_Y)),
        ((TOP_LEFT_W + SLOT_W, TOP_Y), P_CHAMFER_R),
        (P_CHAMFER_R, P_TR),
    ):
        modelspace.add_linear_dim(base=(p2[0], top_dim_y), p1=p1, p2=p2, **dim_kwargs).render()

    # Left vertical edge (28) and slot depth (14).
    modelspace.add_linear_dim(base=(-7, LEFT_H / 2 + CHAMFER_RISE), p1=P_TL, p2=P_CHAMFER_L, angle=90, **dim_kwargs).render()
    modelspace.add_linear_dim(base=(TOP_LEFT_W + 3, SLOT_BOT_Y + SLOT_DEPTH / 2), p1=P_SLOT_L, p2=P_SLOT_BL, angle=90, **dim_kwargs).render()

    # Right side: 34 vertical, 4 wide notch, 6 high notch.
    modelspace.add_linear_dim(base=(TOTAL_W + 7, RIGHT_H / 2), p1=P_TR, p2=(TOTAL_W, 0.0), angle=90, **dim_kwargs).render()
    modelspace.add_linear_dim(base=(TOTAL_W - NOTCH_W / 2, NOTCH_H + 4), p1=P_NOTCH_M, p2=P_NOTCH_TR, **dim_kwargs).render()
    modelspace.add_linear_dim(base=(TOTAL_W + 4, NOTCH_H / 2), p1=P_NOTCH_B, p2=P_NOTCH_M, angle=90, **dim_kwargs).render()

    # Bottom edge. The sketch labels it 41 while the linear chain closes at 37
    # (49 - 4 notch - 8 chamfer run); reproduce the sketch label verbatim.
    modelspace.add_linear_dim(
        base=((CHAMFER_RUN + TOTAL_W) / 2, -7), p1=P_BL, p2=P_NOTCH_B,
        text="41", **dim_kwargs,
    ).render()

    # 41 deg chamfer angle at the bottom-left (downward vertical vs chamfer).
    # The sketch's 41 deg is the chamfer-to-horizontal angle; the drawn arc
    # spans vertical-to-chamfer, so pin the text like the sketch does.
    modelspace.add_angular_dim_2l(
        base=(3.2, 4.0),
        line1=(P_CHAMFER_L, (0.0, CHAMFER_RISE - 10.0)),
        line2=(P_CHAMFER_L, P_BL),
        location=(3.2, 4.0),
        text="41%%d",
        dxfattribs={"layer": "DIM"},
    ).render()

    # Chamfer angle at the slot bottom-right corner (sketch labels it 144 deg).
    chamfer_dir = (math.cos(math.radians(40.0)), math.sin(math.radians(40.0)))
    modelspace.add_angular_dim_3p(
        base=(29.5, 18.5),
        center=P_SLOT_BR,
        p1=P_SLOT_BL,
        p2=(P_SLOT_BR[0] + 10 * chamfer_dir[0], P_SLOT_BR[1] + 10 * chamfer_dir[1]),
        location=(33.0, 24.0),
        text="144%%d",
        dxfattribs={"layer": "DIM"},
    ).render()

    # Chamfer angle at the top-right corner (sketch labels it 140 deg).
    ext_dir = (math.cos(math.radians(140.0)), math.sin(math.radians(140.0)))
    modelspace.add_angular_dim_3p(
        base=(53.0, 38.0),
        center=P_TR,
        p1=(TOTAL_W + 10, CHAMFER_TOP_Y),
        p2=(P_TR[0] + 10 * ext_dir[0], P_TR[1] + 10 * ext_dir[1]),
        location=(53.0, 38.0),
        text="140%%d",
        dxfattribs={"layer": "DIM"},
    ).render()

    return {"document": document}


if __name__ == "__main__":
    gen_dxf()
