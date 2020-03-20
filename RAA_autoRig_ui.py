# Planning #
'''
RIG CLASS

    CREATE JOINTS THREE TIMES
        duplicating and renaming FK IK
        or
        create three times with different names?
        or
        use old script?

        hide joints?

        use locators to mark joints location


    CREATE COLORED CONTROLS WITH ATTRIBUTES
        3 FK Circle Nesting
            cmds.circle(normalX = 1, normalZ = 0, radius = 2)
        1 IK Square
            cmds.curve(degree = 1, point = [(0, 2, 2), (0, 2, -2), (0, -2, -2), (0, -2, 2), (0, 2, 2)], knot = [0, 4, 8, 12, 16])

        1 IK Square pole
            cmds.curve(degree = 1, point = [(0, 1, 1), (0, 1, -1), (0, -1, -1), (0, -1, 1), (0, 1, 1)], knot = [0, 4, 8, 12, 16])

        Move to joint positions
        Freeze transform
            cmds.makeIdentity(apply = True, translate = True, rotate = True,scale = True)
        Add Attributes
            cmds.addAttr(hidden = False, attributeType = "float", longName = "FKIKBlend",niceName = "FK IK Blend",shortName = "FKIKB", defaultValue = 0, maxValue = 1, minValue = 0, keyable = True)

    CREATE IK HANDLE FOR IK JOINTS
        cmds.ikHandle
        cmds.poleVectorConstraint(weight = 1)

    CONSTRAINT JOINTS TO CONTROLS
        cmds.parentConstraint(maintainOffset = True, weight = 1)

    BLEND FK IK NODE EDITOR
        blendColors
            cmds.createNode("blendColors", name = )
'''


# execution #
'''
import ANM_255_142_rarnanjaya as ANM225_142
reload (ANM225_142)
ANM225_142.GenerateLimbUI()
'''


# script #

import maya.cmds as cmds


class GenerateLimbUI:

    main_window = 'generate_limb_window'
    help_window = 'display_help_window'

    def __init__(self):

        # delete UI and its preferences if it exists
        if (cmds.window(self.main_window, exists = True)):
            cmds.deleteUI(self.main_window)
            cmds.windowPref(self.main_window, remove = True)

        # create main window
        cmds.window(self.main_window, title = 'Generate Limb', menuBar = True, widthHeight = [250, 150])


        cmds.menu(label='help', helpMenu = True, postMenuCommand = self.display_help)

        # main column layout
        # cmds.columnLayout(adjustableColumn = True)

        form_layout = cmds.formLayout(numberOfDivisions = 100)

        # limb selection frame layout
        frame_layout = cmds.frameLayout(label = 'Limb Type Selection:', borderVisible = True)

        # radioButtonGrp for limb type
        # self.side_radio = cmds.radioButtonGrp(label =  "Side", numberOfRadioButtons = 3, labelArray3 = ["Right", "Mirror", "Left"], select = 2)
        # redundant

        # radioButtonGrp for limb type
        self.type_radio = cmds.radioButtonGrp(numberOfRadioButtons = 2, labelArray2 = ['Arm', 'Leg'], select = 1,
                                              adjustableColumn2 = True, columnAttach2 = ['left','right'], columnOffset2 = [40,40],
                                              backgroundColor = [0.22,0.22,0.22])


        # go back to layout top level
        cmds.setParent(topLevel = True)


        # button for locator creation
        locator_button = cmds.button(label = 'Create Locators', command = lambda generate_limb: self.query_UI(False))


        # button for limb generation
        generate_button = cmds.button(label = 'Generate Limbs', command = lambda generate_limb: self.query_UI(True))


        cmds.formLayout(form_layout, edit=True,
                attachForm		= [(frame_layout, 'top', 5), (frame_layout, 'left', 5), (frame_layout, 'right', 5), (locator_button, 'left', 5), (locator_button, 'right', 5), (generate_button, 'left', 5), (generate_button, 'right', 5), (generate_button, 'bottom', 5)],
                attachControl	= [(frame_layout, 'bottom', 5, locator_button), (generate_button, 'top', 5, locator_button)],
                attachPosition	= [(locator_button, 'top', 5, 50), (locator_button, 'bottom', 0, 75)])

        # show window
        cmds.showWindow(self.main_window)

    def display_help(self, *args):
        # method to show help pop up when help menu is pressed

        help_message = '''Select a limb type, then click Create Locators.
Arrange the locators to match your character.
Select a starting joint, then click Generate Limb.'''


        # delete UI and its preferences if it exists
        if (cmds.window(self.help_window, exists = True)):
            cmds.deleteUI(self.help_window)
            cmds.windowPref(self.help_window, remove = True)


        help_window = cmds.window(self.help_window, title = 'Help', sizeable = False)

        cmds.columnLayout()
        cmds.text(label = help_message, width = 300, height = 75)

        cmds.showWindow(self.help_window)



    def query_UI(self, generate_limb):
        # method to query control values from UI

        #limb_side   = cmds.radioButtonGrp(self.side_radio, query = True, select = True)
        limb_type   = cmds.radioButtonGrp(self.type_radio, query = True, select = True)

        print(limb_type)

        if generate_limb:
            GenerateLimb(limb_type)
        else:
            arrange_locator(limb_type)