'''
works if chain aim using +X axis
cycle on bcl_lock and jnt_C.tx
'''
import pymel.core as pm

selected = pm.ls(os = True)

class CreateIK:

    def __init__(self, IK_name, jnt_A, jnt_B, jnt_C, ctrl_IK):

        # this name will be used throughout the class as a naming convention
        self.IK_name = IK_name

        self.jnt_A = jnt_A

        self.jnt_B = jnt_B

        self.jnt_C = jnt_C

        self.ctrl_IK = ctrl_IK

        self.rev_weight = False

        self.poc_hdl_IK = False

    def create_IK(self):

        # create duplicate IK chain for scaling
        self.jnt_A_scale = pm.duplicate(self.jnt_A, name = self.jnt_A.name(long = None) + '_scale', parentOnly = True)[0]
        self.jnt_B_scale = pm.duplicate(self.jnt_B, name = self.jnt_B.name(long = None) + '_scale', parentOnly = True)[0]
        self.jnt_C_scale = pm.duplicate(self.jnt_C, name = self.jnt_C.name(long = None) + '_scale', parentOnly = True)[0]
        pm.parent(self.jnt_B_scale, self.jnt_A_scale)
        pm.parent(self.jnt_C_scale, self.jnt_B_scale)

        # create IK handle
        hdl_IK_name = 'ikh_' + self.IK_name
        self.hdl_IK = pm.ikHandle(name = hdl_IK_name, startJoint = self.jnt_A, endEffector = self.jnt_C)[0]


    def create_PV(self):

        # getTranslation returns vector
        jnt_A_vector = self.jnt_A.getTranslation(space = 'world')
        jnt_B_vector = self.jnt_B.getTranslation(space = 'world')
        jnt_C_vector = self.jnt_C.getTranslation(space = 'world')

        jnt_A_B_vector = jnt_B_vector - jnt_A_vector
        jnt_A_C_vector = jnt_C_vector - jnt_A_vector


        # * means vector dot operation
        dot_vector = jnt_A_B_vector * jnt_A_C_vector

        # dot product is an abstract projection value, not a magnitude(length) or angle
        # dot product = |A| x |B| x cos(a)
        # dot product = |A| x |B| x 1, if both A and B are codirectional (a = 0 degree)
        # dot product / |B| = |A|, |A| is projection_length
        projection_length = float(dot_vector) / float(jnt_A_C_vector.length())

        # Any nonzero vector can be divided by its length to form a unit vector.
        # normal = vector / length
        jnt_A_C_normal = jnt_A_C_vector.normal()

        # normal * length = vector, on the direction of normal, and the magnitude of length
        projection_vector = jnt_A_C_normal * projection_length

        # arrow_vector is a vector between A & C, through B
        arrow_vector = jnt_A_B_vector - projection_vector
        # PV will be 0.5 arrow length away from jnt B
        arrow_vector *= 0.5
        final_vector = arrow_vector + jnt_B_vector

        self.pv_IK = pm.spaceLocator()
        self.pv_IK.setTranslation(final_vector, space = 'world')

        pm.poleVectorConstraint(self.pv_IK, self.hdl_IK)


    def soft_IK(self):
        '''
        Formula

        y = {
              dsoft( 1 - E^(( da-x )/dsoft) ) + da   (da <= x)
                                                               }

        da = dchain - dsoft
        dchain = sum of bone lengths
        dsoft = user set soft distancqe (how far the effector should fall behind)
        x = distance between root and ik
        '''
        # Euler's Number
        E = 2.71828

        # calculate dchain
        dchain = self.jnt_B.tx.get() + self.jnt_C.tx.get()

        # add soft IK attribute
        self.ctrl_IK.addAttr('softIK', niceName = 'Soft IK', shortName = 'sik', attributeType = 'float', defaultValue = 0,
                   softMaxValue = 20, softMinValue = 0, maxValue = 50, minValue = 0, keyable = True, hidden = False)

        # create setRange node to convert softIK value to softIK distance (dsoft)
        set_rng_dsoft = pm.createNode('setRange', name = 'set_rng_' + self.IK_name + '_dsoft')
        set_rng_dsoft.oldMax.oldMaxX.set(50)
        set_rng_dsoft.max.maxX.set(5)
        set_rng_dsoft.min.minX.set(0.001)
        self.ctrl_IK.softIK >> set_rng_dsoft.value.valueX

        # create plusMinusAverage to calculate da (= dchain - dsoft)
        pma_da = pm.createNode('plusMinusAverage', name = 'pma_' + self.IK_name + '_da')
        pma_da.operation.set(2)
        pma_da.input1D.input1D[0].set(dchain)
        set_rng_dsoft.outValue.outValueX >> pma_da.input1D.input1D[1]

        # create distanceBetween to calculate x
        dbw_x = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_x')
        self.jnt_A_scale.worldMatrix.worldMatrix[0] >> dbw_x.inMatrix1
        self.ctrl_IK.worldMatrix.worldMatrix[0] >> dbw_x.inMatrix2

        # create plusMinusAverage to calculate da-x
        pma_da_min_x = pm.createNode('plusMinusAverage', name = 'pma_' + self.IK_name + '_da_min_x')
        pma_da_min_x.operation.set(2)
        pma_da.output1D >> pma_da_min_x.input1D.input1D[0]
        dbw_x.distance >> pma_da_min_x.input1D.input1D[1]

        # create multiplyDivide to calculate da-x / dsoft
        mdv_div_dsoft = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_div_dsoft')
        mdv_div_dsoft.operation.set(2)
        pma_da_min_x.output1D >> mdv_div_dsoft.input1.input1X
        set_rng_dsoft.outValue.outValueX >> mdv_div_dsoft.input2.input2X

        # create multiplyDivide to calculate e^(da-x / dsoft)
        mdv_e_pow = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_e_pow')
        mdv_e_pow.operation.set(3)
        mdv_e_pow.input1.input1X.set(E)
        mdv_div_dsoft.output.outputX >> mdv_e_pow.input2.input2X

        # create plusMinusAverage to calculate 1 - e^(da-x / dsoft)
        pma_1_min = pm.createNode('plusMinusAverage', name = 'pma_' + self.IK_name + '_1_min')
        pma_1_min.operation.set(2)
        pma_1_min.input1D.input1D[0].set(1)
        mdv_e_pow.output.outputX >> pma_1_min.input1D.input1D[1]

        # create multiplyDivide to calculate dsoft * (1 - e^(da-x / dsoft))
        mdv_dsoft_mul = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_dsoft_mul')
        set_rng_dsoft.outValue.outValueX >> mdv_dsoft_mul.input1.input1X
        pma_1_min.output1D >> mdv_dsoft_mul.input2.input2X

        # create plusMinusAverage to calculate dsoft * (1 - e^(da-x / dsoft)) + da
        pma_add_da = pm.createNode('plusMinusAverage', name = 'pma_' + self.IK_name + '_add_da')
        mdv_dsoft_mul.output.outputX >> pma_add_da.input1D.input1D[0]
        pma_da.output1D >> pma_add_da.input1D.input1D[1]

        # create condition to calculate da <= x
        cnd = pm.createNode('condition', name = 'cnd_' + self.IK_name)
        # operation: less or equal
        cnd.operation.set(5)
        pma_da.output1D >> cnd.firstTerm
        dbw_x.distance >> cnd.secondTerm
        pma_add_da.output1D >> cnd.colorIfTrue.colorIfTrueR
        dbw_x.distance >> cnd.colorIfFalse.colorIfFalseR

        # create multiplyDivide to calculate cnd / x
        self.mdv_div_x = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_div_x')
        self.mdv_div_x.operation.set(2)
        cnd.outColor.outColorR >> self.mdv_div_x.input1.input1X
        dbw_x.distance >> self.mdv_div_x.input2.input2X

        # create reverse node to calculate point contraint weights
        self.rev_weight = pm.createNode('reverse', name = 'rev_' + self.IK_name + '_weight')
        self.mdv_div_x.output.outputX >> self.rev_weight.input.inputX

        self.combo('soft')


    def stretch_IK(self):
        # create stretch, nudge, nudgeLR, and lock attributes

        # add stretch attribute
        self.ctrl_IK.addAttr('stretch', niceName = 'Stretch', shortName = 'strt', attributeType = 'float', defaultValue = 0,
                             softMaxValue = 1, softMinValue = 0, keyable = True, hidden = False)

        # add nudge attribute
        self.ctrl_IK.addAttr('nudge', niceName = 'Nudge', shortName = 'ndg', attributeType = 'float', defaultValue = 0,
                             keyable = True, hidden = False)

        # add nudgeLR IK attribute
        self.ctrl_IK.addAttr('nudgeLR', niceName = 'Nudge LR', shortName = 'nlr', attributeType = 'float', defaultValue = 0,
                             maxValue = 10, minValue = -10, keyable = True, hidden = False)

        # add elbowLock IK attribute
        self.ctrl_IK.addAttr('elbowLock', niceName = 'Elbow Lock', shortName = 'elbwlck', attributeType = 'float', defaultValue = 0,
                             maxValue = 1, minValue = 0, keyable = True, hidden = False)


        # create distanceBetween to measure from jnt_A_scale to jnt_B_scale
        dbw_A_B = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_A_B')
        self.jnt_A_scale.worldMatrix.worldMatrix[0] >> dbw_A_B.inMatrix1
        self.jnt_B_scale.worldMatrix.worldMatrix[0] >> dbw_A_B.inMatrix2

        # create distanceBetween to measure from jnt_B_scale to jnt_C_scale
        dbw_B_C = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_BC')
        self.jnt_B_scale.worldMatrix.worldMatrix[0] >> dbw_B_C.inMatrix1
        self.jnt_C_scale.worldMatrix.worldMatrix[0] >> dbw_B_C.inMatrix2

        # create distanceBetween to measure from jnt_A_scale to pv_IK
        dbw_A_pv = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_A_pv')
        self.jnt_A_scale.worldMatrix.worldMatrix[0] >> dbw_A_pv.inMatrix1
        self.pv_IK.worldMatrix.worldMatrix[0] >> dbw_A_pv.inMatrix2

        # create distanceBetween to measure from pv_IK to ctrl_IK
        dbw_pv_ctrl = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_pv_ctrl')
        self.pv_IK.worldMatrix.worldMatrix[0] >> dbw_pv_ctrl.inMatrix1
        self.ctrl_IK.worldMatrix.worldMatrix[0] >> dbw_pv_ctrl.inMatrix2

        # create distanceBetween to measure from jnt_A_scale to ctrl_IK (total distance)
        dbw_A_ctrl = pm.createNode('distanceBetween', name = 'dbw_' + self.IK_name + '_A_ctrl')
        self.jnt_A_scale.worldMatrix.worldMatrix[0] >> dbw_A_ctrl.inMatrix1
        self.ctrl_IK.worldMatrix.worldMatrix[0] >> dbw_A_ctrl.inMatrix2


        # create addDoubleLinear to sum dbw_A_B and dbw_B_C
        adl_A_B_C = pm.createNode('addDoubleLinear', name = 'adl_' + self.IK_name + '_A_B_C')
        dbw_A_B.distance >> adl_A_B_C.input1
        dbw_B_C.distance >> adl_A_B_C.input2

        # create multiplyDivide to calculate dbw_A_ctrl / adl_A_B_C
        mdv_A_ctrl_div_A_B_C = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_A_ctrl_div_A_B_C')
        mdv_A_ctrl_div_A_B_C.operation.set(2)
        dbw_A_ctrl.distance >> mdv_A_ctrl_div_A_B_C.input1.input1X
        adl_A_B_C.output >> mdv_A_ctrl_div_A_B_C.input2.input2X

        # create condition to calculate if dbw_A_ctrl is longer than adl_A_B_C (if total distance to ctrl_IK is longer than normal)
        cnd_stretch = pm.createNode('condition', name = 'cnd_' + self.IK_name + '_stretch')
        # operation: greater than
        cnd_stretch.operation.set(2)
        dbw_A_ctrl.distance >> cnd_stretch.firstTerm
        adl_A_B_C.output >> cnd_stretch.secondTerm
        mdv_A_ctrl_div_A_B_C.output.outputX >> cnd_stretch.colorIfTrue.colorIfTrueR
        cnd_stretch.colorIfFalse.colorIfFalseR.set(1)

        # create blendColors to blend 1 with cnd_stretch
        bcl_stretch = pm.createNode('blendColors', name = 'bcl_' + self.IK_name + '_stretch')
        cnd_stretch.outColor.outColorR >> bcl_stretch.color1.color1R
        bcl_stretch.color2.color2R.set(1)
        self.ctrl_IK.stretch >> bcl_stretch.blender


        # create multiplyDivide to reduce ctrl_IK.nudge value
        mdv_nudge = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_nudge')
        self.ctrl_IK.nudge >> mdv_nudge.input1.input1X
        mdv_nudge.input2.input2X.set(0.001)

        # create addDoubleLinear to sum bcl_stretch and nudge
        adl_nudge = pm.createNode('addDoubleLinear', name = 'adl_' + self.IK_name + '_nudge')
        mdv_nudge.output.outputX >> adl_nudge.input1
        bcl_stretch.output.outputR >> adl_nudge.input2


        # create setRange node to remap ctrl_IK.nudgeLR (-10 - 10) to (0 - 1)
        set_rng_nudgeLR = pm.createNode('setRange', name = 'set_rng_' + self.IK_name + '_nudgeLR')
        set_rng_nudgeLR.oldMax.oldMaxX.set(10)
        set_rng_nudgeLR.oldMin.oldMinX.set(-10)
        set_rng_nudgeLR.max.maxX.set(1)
        set_rng_nudgeLR.min.minX.set(0)
        self.ctrl_IK.nudgeLR >> set_rng_nudgeLR.value.valueX

        # create blendColors to blend 1 with cnd_stretch
        bcl_nudgeLR = pm.createNode('blendColors', name = 'bcl_' + self.IK_name + '_nudgeLR')
        bcl_nudgeLR.color1.color1R.set(1)
        bcl_nudgeLR.color1.color1G.set(-1)
        bcl_nudgeLR.color2.color2R.set(-1)
        bcl_nudgeLR.color2.color2G.set(1)
        set_rng_nudgeLR.outValue.outValueX >> bcl_nudgeLR.blender

        # create plusMinusAverage to add bcl_nudgeLR value to adl_nudge
        pma_nudgeLR = pm.createNode('plusMinusAverage', name = 'pma_' + self.IK_name + '_nudgeLR')
        adl_nudge.output >> pma_nudgeLR.input2D.input2D[0].input2Dx
        adl_nudge.output >> pma_nudgeLR.input2D.input2D[0].input2Dy
        bcl_nudgeLR.output.outputR >> pma_nudgeLR.input2D.input2D[1].input2Dx
        bcl_nudgeLR.output.outputG >> pma_nudgeLR.input2D.input2D[1].input2Dy


        # create multiplyDivide to calculate dbw_A_ctrl / adl_A_B_C
        mdv_lock = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_lock')
        mdv_lock.operation.set(2)
        dbw_A_pv.distance >> mdv_lock.input1.input1X
        dbw_pv_ctrl.distance >> mdv_lock.input1.input1Y
        dbw_A_B.distance >> mdv_lock.input2.input2X
        dbw_B_C.distance >> mdv_lock.input2.input2Y

        # create blendColors to blend mdv_lock with pma_nudgeLR
        bcl_lock = pm.createNode('blendColors', name = 'bcl_' + self.IK_name + '_lock')
        mdv_lock.output >> bcl_lock.color1
        pma_nudgeLR.output2D.output2Dx >> bcl_lock.color2.color2R
        pma_nudgeLR.output2D.output2Dy >> bcl_lock.color2.color2G
        self.ctrl_IK.elbowLock >> bcl_lock.blender

        # create multiplyDivide to return actual distance
        mdv_actual = pm.createNode('multiplyDivide', name = 'mdv_' + self.IK_name + '_actual')
        bcl_lock.output >> mdv_actual.input1
        self.jnt_B_scale.tx >> mdv_actual.input2.input2X
        self.jnt_C_scale.tx >> mdv_actual.input2.input2Y

        mdv_actual.output.outputX >> self.jnt_B.tx
        mdv_actual.output.outputY >> self.jnt_C.tx

        self.combo('stretch')


    def combo(self, modifier):

        soft = 'soft'
        stretch = 'stretch'

        if self.poc_hdl_IK and self.rev_weight:
            # if stretch_IK() or soft_IK() has been called
            # stretch overrides soft
            print('if stretch_IK() or soft_IK() has been called')

            # create condition node, if ctrl_IK.stretch > 0, then return 0, else return reverse soft value
            cnd_soft = pm.createNode('condition', name = 'cnd_' + self.IK_name + '_soft')
            # operation: greater than
            cnd_soft.operation.set(2)
            self.ctrl_IK.stretch >> cnd_soft.firstTerm
            cnd_soft.secondTerm.set(0)
            cnd_soft.colorIfTrue.colorIfTrueR.set(0)
            self.rev_weight.output.outputX >> cnd_soft.colorIfFalse.colorIfFalseR

            poc_hdl_IK_attr_W0 = self.poc_hdl_IK.attr(self.jnt_A_scale.name(long = None) + 'W0')
            poc_hdl_IK_attr_W1 = self.poc_hdl_IK.attr(self.ctrl_IK.name(long = None) + 'W1')

            cnd_soft.outColor.outColorR >> poc_hdl_IK_attr_W0

            if modifier == soft:
                # if stretch_IK() has been called, and soft_IK() is being called
                self.mdv_div_x.output.outputX >> poc_hdl_IK_attr_W1

        else:
            # if stretch_IK() or soft_IK() has not been called
            print('if stretch_IK() or soft_IK() has not been called')

            # point contraint IK handle to both jnt_A_scale and ctrl_IK
            self.poc_hdl_IK = pm.pointConstraint(self.jnt_A_scale, self.ctrl_IK, self.hdl_IK, maintainOffset = False)
            poc_hdl_IK_attr_W0 = self.poc_hdl_IK.attr(self.jnt_A_scale.name(long = None) + 'W0')
            poc_hdl_IK_attr_W1 = self.poc_hdl_IK.attr(self.ctrl_IK.name(long = None) + 'W1')

            if modifier == soft:
                # if stretch_IK() has not been called, solo soft
                print('if stretch_IK() has not been called')
                self.rev_weight.output.outputX >> poc_hdl_IK_attr_W0
                self.mdv_div_x.output.outputX >> poc_hdl_IK_attr_W1

            if modifier == stretch:
                # if soft_IK() has not been called, solo stretch
                print('if soft_IK() has not been called')
                poc_hdl_IK_attr_W0.set(0)


# del IK_ins_01

IK_ins_01 = CreateIK('IK_ins_01', selected[0], selected[1], selected[2], selected[3])
IK_ins_01.create_IK()
IK_ins_01.create_PV()
IK_ins_01.stretch_IK()
IK_ins_01.soft_IK()

# IK_ins_02 = CreateIK('IK_ins_02', selected[4], selected[5], selected[6], selected[7])
# IK_ins_02.create_IK()
# IK_ins_02.create_PV()
# IK_ins_02.soft_IK()
# IK_ins_02.stretch_IK()