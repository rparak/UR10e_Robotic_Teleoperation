# Filter Paramteres: Limit (Boundaries [-,+]), Number of total periods
#   Position
CONST_FILTER_POS_LIMIT = [[-22.5, 22.5], [0.0, 45.0], [-45.0, 0.0]]
CONST_FILTER_POS_NUM_OF_DATA = 100
#   Fingers Bend
CONST_FILTER_FINGERS_BEND_LIMIT = [[5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0]]
CONST_FILTER_FINGERS_BEND_NUM_OF_DATA = 25

# Time step inside threads (Essential Reality P5)
CONST_TIME_STEP  = 0.004

# Initialization of Constants:-+
#   ABB Robot (IRB 1200)
#       Workspace
CONST_ABB_WORKSPACE          = [360.0,360.0,360.0]
#       Position and Orientation
CONST_ABB_CARTES_POS_HOME    = [450.0,0.0,500.0]
CONST_ABB_CARTES_ORIENT_HOME = [0.0,0.0,1.0,0.0]
#   Universal Robots (UR10e)
#       Workspace
#           Old:
#CONST_UR_WORKSPACE          = [800.0, 400.0, 300.0]
#           New:
CONST_UR_WORKSPACE          = [760.0, 400.0, 200.0]
#       Position and Orientation
#   Old:
#CONST_UR_CARTES_POS_HOME    = [0.0, -600.0, 500.0]
#CONST_UR_CARTES_ORIENT_HOME = [0.0, 3.14, 0.0]
#   New:
CONST_UR_CARTES_POS_HOME    = [0.0, -700.0, 515.0]
CONST_UR_CARTES_ORIENT_HOME = [0.0, 3.142, 0.0]
#   Essential Reality P5 Glove
CONST_SENSOR_POS_WORKSPACE  = CONST_FILTER_POS_LIMIT