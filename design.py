import cadquery as cq


def in_to_cm(inches: float):
    return 2.54 * inches


std_thickness = in_to_cm(2)
table_depth = 60
table_length = 120
table_height = 86
table_top_thickness = 2
leg_width = std_thickness
panel_height = 20
drawer_widths = [70, 35]
drawer_height = 12
m5_diameter = 0.5
bolt_length = 5

panel_thickness = std_thickness
side_panel_length = table_depth - 2 * leg_width
front_panel_length = table_length - 2 * leg_width
front_panel_excess_length = front_panel_length - sum(drawer_widths)
drawer_lateral_border_width = front_panel_excess_length / (len(drawer_widths) + 1)
leg_length = table_height - table_top_thickness

shelf_backboard_height = 15
wall_frame_board_width = in_to_cm(4)
wall_frame_board_depth = std_thickness
shelf_height = 185
shelf_depth = 25
wall_frame_screw_inset = 3
wall_frame_screw_spacing = wall_frame_board_width - wall_frame_screw_inset
wall_frame_height = (shelf_height + shelf_backboard_height - table_height + table_top_thickness + panel_height)


def make_shelf():
    shelf = cq.Workplane().box(shelf_depth, table_length, std_thickness)
    hole_heights = [wall_frame_screw_inset]
    hole_heights.append((shelf_depth / 2))
    hole_locations = [(-shelf_depth / 2 + hh, side*(table_length-std_thickness)/2) for hh in
                      hole_heights for side in [1, -1]]
    # hole_locations = [(shelf_depth/2 - wall_frame_screw_inset, 0)]
    shelf = shelf.faces('>Z').workplane(centerOption="CenterOfBoundBox").pushPoints(hole_locations).hole(
        m5_diameter / 2, bolt_length)
    shelf.faces('>Z').edges('%CIRCLE').edges('<X').edges('>Y').tag('screw_front_left')
    shelf.faces('>Z').edges('%CIRCLE').edges('>X').edges('>Y').tag('screw_rear_left')
    shelf.faces('>Z').edges('%CIRCLE').edges('<X').edges('<Y').tag('screw_front_right')
    shelf.faces('>Z').edges('%CIRCLE').edges('>X').edges('<Y').tag('screw_rear_right')
    return shelf

def make_shelf_support():
    board = cq.Workplane().box(shelf_depth, std_thickness, wall_frame_board_width)
    hole_heights = [wall_frame_screw_inset]
    hole_heights.append((wall_frame_board_width - wall_frame_screw_inset))
    hole_locations = [(0, wall_frame_board_width / 2 - hh) for hh in
                      hole_heights]
    board = board.faces('>X').workplane().pushPoints(hole_locations).hole(m5_diameter / 2, bolt_length)
    hole_heights = [wall_frame_screw_inset]
    hole_heights.append((shelf_depth/2))
    hole_locations = [(-shelf_depth/2 + hh, 0) for hh in
                      hole_heights]
    # hole_locations = [(shelf_depth/2 - wall_frame_screw_inset, 0)]
    board = board.faces('<Z').workplane(centerOption="CenterOfBoundBox").pushPoints(hole_locations).hole(m5_diameter / 2, bolt_length)
    board.faces('<Z').edges('%CIRCLE').edges('<X').tag('screw_front')
    board.faces('<Z').edges('%CIRCLE').edges('>X').tag('screw_rear')
    board.faces('>X').edges('%CIRCLE').edges('>Z').tag('screw_top')
    board.faces('>X').edges('%CIRCLE').edges('<Z').tag('screw_bottom')
    # board.faces('<Z').edges('%CIRCLE').edges('<X').edges('<Y').tag('screw_front_right')
    return board

def make_leg():
    leg = cq.Workplane('XY').rect(leg_width, leg_width).extrude(leg_length)
    return leg


def make_side_panel():
    return cq.Workplane().box(side_panel_length, panel_thickness, panel_height)


def make_rear_panel():
    return cq.Workplane().box(front_panel_length, panel_thickness, panel_height)


def make_face_frame():
    face_frame = make_rear_panel()
    drawer_x = -front_panel_length / 2
    for drawer_width in drawer_widths:
        drawer_x += drawer_width / 2 + drawer_lateral_border_width
        face_frame = face_frame.faces('>Y').workplane(offset=1, centerOption="CenterOfBoundBox").move(drawer_x, 0).rect(
            drawer_width, drawer_height).cutThruAll()
        drawer_x += drawer_width / 2
    return face_frame


def make_wall_frame_vertical_board():
    board = cq.Workplane().box(wall_frame_board_depth, wall_frame_board_width, wall_frame_height)
    # board = board.faces('>X').workplane().hole(m5_diameter/2)
    hole_heights = [wall_frame_screw_inset]
    hole_heights.append((wall_frame_board_width - wall_frame_screw_inset))
    hole_heights.append((wall_frame_height-hole_heights[0]))
    hole_heights.append((wall_frame_height-hole_heights[1]))
    hole_locations = [(wall_frame_board_width/2-std_thickness/2, wall_frame_height/2 - hh) for hh in hole_heights]
    board = board.faces('>X').workplane().pushPoints(hole_locations).hole(m5_diameter/2, bolt_length)
    # board.faces('>X').edges('%CIRCLE').tag(f'screws')

    board.faces('>X').edges('%CIRCLE').edges('>Z').tag(f'screw0')
    board.faces('>X').edges('%CIRCLE').edges('not(>Z)').edges('>Z').tag(f'screw1')
    # board.faces('>X').edges('%CIRCLE').edges('>Z[-1]').tag(f'screw1')
    # board.faces('>X').edges('%CIRCLE').edges(f'>Z[1]').tag(f'screw1')
    # board.faces('>X').edges('%CIRCLE').edges(f'<Z').tag(f'screw3')
    return board


def make_wall_frame_horizontal_board():
    width = table_length - wall_frame_board_width * 2
    return cq.Workplane().box(wall_frame_board_depth, width, wall_frame_board_width)


table_top = cq.Workplane().box(table_depth, table_length, table_top_thickness)

wood_color = cq.Color(203 / 255, 175 / 255, 117 / 255)
white = cq.Color('white')

top_assy = (
    cq.Assembly(color=wood_color)
        .add(make_wall_frame_vertical_board(), name='v_l')
        .add(make_wall_frame_horizontal_board(), name='h_t')
        .constrain('v_l@faces@+Z', 'h_t@faces@+Z', 'Axis')
        .constrain('v_l@faces@<Y', 'h_t@faces@<Y', 'Axis')
        .constrain('v_l@vertices@>(1,-1,1)', 'h_t@vertices@>(1,-1,-1)', 'Point')
        .add(make_wall_frame_horizontal_board(), name='h_b')
        .constrain('v_l@faces@+Z', 'h_b@faces@+Z', 'Axis')
        .constrain('v_l@faces@<Y', 'h_b@faces@<Y', 'Axis')
        .constrain('v_l@vertices@>(1,-1,-1)', 'h_b@vertices@>(1,-1,1)', 'Point')
    .add(make_wall_frame_vertical_board(), name='v_r')
    .constrain('v_l@faces@+Z', 'v_r@faces@+Z', 'Axis')
        .constrain('v_l@faces@<Y', 'v_r@faces@<Y', 'Axis')
        .constrain('h_t@vertices@>(1,1,-1)', 'v_r@vertices@>(1,-1,-1)', 'Point')
    .add(make_shelf(), name='shelf')
    .add(make_shelf_support(), name='shelf_support_left')
    .constrain('shelf?screw_front_left', 'shelf_support_left?screw_front', 'Point')
    .constrain('shelf?screw_rear_left', 'shelf_support_left?screw_rear', 'Plane')
        .add(make_shelf_support(), name='shelf_support_right')
        .constrain('shelf?screw_front_right', 'shelf_support_right?screw_front', 'Point')
        .constrain('shelf?screw_rear_right', 'shelf_support_right?screw_rear', 'Plane')
        .constrain('v_l?screw0', 'shelf_support_right?screw_top', 'Point')
        .constrain('v_l?screw1', 'shelf_support_right?screw_bottom', 'Plane')
        # .constrain('v_r?screw3', 'shelf_support_right?screw_top', 'Point')

    # .constrain('shelf@faces@+Z', 'shelf_support_left@faces@+Z', 'Axis')
    # .constrain('h_t', )
)
top_assy.solve()

table_assy = (
    cq.Assembly(color=white)
        .add(table_top, name='table_top', loc=cq.Location((0, 0, 0)), color=wood_color)
        .add(make_leg(), name='leg1')
        .add(make_leg(), name='leg2')
        .add(make_leg(), name='leg3')
        .add(make_leg(), name='leg4')
        .constrain('table_top@faces@<Z', 'leg1@faces@>Z', 'Axis')
        .constrain('table_top@faces@>Y', 'leg1@faces@<Y', 'Axis')
        .constrain('table_top@vertices@>(-1,-1,-1)', 'leg1@vertices@>(-1,-1,1)', 'Point')
        .constrain('table_top@faces@<Z', 'leg2@faces@>Z', 'Axis')
        .constrain('table_top@faces@>Y', 'leg2@faces@<Y', 'Axis')
        .constrain('table_top@vertices@>(1,-1,-1)', 'leg2@vertices@>(1,-1,1)', 'Point')
        .constrain('table_top@faces@<Z', 'leg3@faces@>Z', 'Axis')
        .constrain('table_top@faces@>Y', 'leg3@faces@<Y', 'Axis')
        .constrain('table_top@vertices@>(-1,1,-1)', 'leg3@vertices@>(-1,1,1)', 'Point')
        .constrain('table_top@faces@<Z', 'leg4@faces@>Z', 'Axis')
        .constrain('table_top@faces@>Y', 'leg4@faces@<Y', 'Axis')
        .constrain('table_top@vertices@>(1,1,-1)', 'leg4@vertices@>(1,1,1)', 'Point')
)
(table_assy.add(make_side_panel(), name='side_panel1')
 .constrain('table_top@faces@<Z', 'side_panel1@faces@>Z', 'Axis')
 .constrain('table_top@faces@<Y', 'side_panel1@faces@>Y', 'Axis')
 .constrain('leg1@vertices@>(1,1,1)', 'side_panel1@vertices@>(-1,1,1)', 'Point')
 )
(table_assy.add(make_side_panel(), name='side_panel2')
 .constrain('table_top@faces@<Z', 'side_panel2@faces@>Z', 'Axis')
 .constrain('table_top@faces@<Y', 'side_panel2@faces@>Y', 'Axis')
 .constrain('leg3@vertices@>(1,1,1)', 'side_panel2@vertices@>(-1,1,1)', 'Point')
 )
(table_assy.add(make_face_frame(), name='face_frame')
 .constrain('table_top@faces@<Z', 'face_frame@faces@>Z', 'Axis')
 .constrain('table_top@faces@>Y', 'face_frame@faces@>X', 'Axis')
 .constrain('leg4@vertices@>(-1,-1,1)', 'face_frame@vertices@>(-1,1,1)', 'Point')
 )
(table_assy.add(make_rear_panel(), name='rear_panel')
 .constrain('table_top@faces@<Z', 'rear_panel@faces@>Z', 'Axis')
 .constrain('table_top@faces@>Y', 'rear_panel@faces@>X', 'Axis')
 .constrain('leg3@vertices@>(1,-1,1)', 'rear_panel@vertices@>(-1,1,1)', 'Point')
 )

(table_assy.add(top_assy, name='top_assy')
.constrain('table_top', table_top.faces('+Y').val(), 'top_assy', top_assy.objects['v_l'].obj.faces('+Y').val(), 'Axis')
 .constrain('table_top', table_top.vertices('>(-1,-1,1)').val(), 'top_assy', top_assy.objects['v_l'].obj.vertices('>(1,1,1)').val(), 'Point')
 .constrain('table_top', table_top.faces('+Z').val(), 'top_assy', top_assy.objects['v_l'].obj.faces('+Z').val(), 'Axis')

 )
table_assy.solve()

# main_assy = (
#     cq.Assembly()
#     .add(table_assy.obj, name='table_assy')
#     .add(top_assy.obj, name='top_assy')
#     .constrain('table_assy@faces@+Z', 'top_assy@faces@+Z', 'Axis')
# )
# main_assy.solve()
# (assy.add(top_assy, name='top_assy')
#  .constrain('rear_panel@faces@+Z', 'rear_panel@faces@+Z', 'Axis'))
show_object(table_assy)
# legs = table_top.faces("<Z").rect(table_depth-leg_width, table_length-leg_width, forConstruction=True).vertices().rect(leg_width, leg_width).extrude(-leg_length)
