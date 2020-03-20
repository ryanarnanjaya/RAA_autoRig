'''
ribbon
'''
import pymel.core as pm
import sys
# print(sys.path)
i = r'B:\Documents\RAA_autoRig'
if i not in sys.path:
    sys.path.append(i)

import RAA_autoRig_srtBuf as sb
import RAA_autoRig_createCtrl as cc

# selected = pm.ls(os = True)
# ribbon_segment, ribbon_length, aim_axis, up_axis
class CreateRibbon:

    def __init__(self, ribbon_name, ribbon_segment):

        # this name will be used throughout the class as a naming convention
        self.ribbon_name = ribbon_name

        self.ribbon_segment = ribbon_segment

    def create_nurbs(self):

        self.nurbs = pm.nurbsPlane(name = 'geo_' + self.ribbon_name, pivot = [0, 0, 0], axis = [0, 1, 0], width = 1, lengthRatio = self.ribbon_segment, degree = 3, ch = False)[0]
        self.nurbs.setRotation([0, 90, 0], space = 'world')
        pm.makeIdentity(self.nurbs, a = True, rotate = True)

        # rebuild nurbs to reduce CVs
        pm.rebuildSurface(self.nurbs, replaceOriginal = True, rebuildType = 0, endKnots = 1, keepRange = 0, keepControlPoints = 0, keepCorners = 0,
                          spansU = 1, degreeU = 1, spansV = self.ribbon_segment, degreeV = 3, ch = False)

    def add_flc(self):
        # add follicles in each segments

        # calculate follicle v coordinates
        flc_v_distance = 1.0 / self.ribbon_segment
        flc_v_start = flc_v_distance / 2.0

        # create a list of v coordinates, range() only works with int
        flc_v = [flc_v_start]
        for i in range(self.ribbon_segment - 1):
            flc_v.append(flc_v[-1] + flc_v_distance)

        # create a list of follicles for other methods
        self.flc_list = []

        for segment, v in enumerate(flc_v, 1):

            # add 1 to segment so that padding starts from 001
            flc_name = 'flc_{}_{:03d}'.format(self.ribbon_name, segment + 1)
            flc_shape_name = '{}Shape'.format(flc_name)

            # create an empty transform then the follicle shape node
            flc = pm.createNode('transform', name = flc_name)
            self.flc_list.append(flc)
            flc_shape = pm.createNode('follicle', name = flc_shape_name, p = flc)

            # connect attributes to attach follicle
            self.nurbs.worldMatrix.worldMatrix[0] >> flc_shape.inputWorldMatrix
            self.nurbs.local >> flc_shape.inputSurface
            flc_shape.outTranslate >> flc.translate
            flc_shape.outRotate >> flc.rotate

            # position follicle based on calculated coordinates
            flc_shape.parameterU.set(0.5)
            flc_shape.parameterV.set(v)



    def add_ctrl_jnt(self):

        for pad, flc in enumerate(self.flc_list, 1):
            pm.select(clear = True)
            flc_tra = flc.getTranslation()

            # create control
            control_name = 'ctrl_{}_{:03d}'.format(self.ribbon_name, pad)
            control = cc.CreateCtrl(name = control_name, side = 'L', shape = 'circle', color = 6)
            control_obj = control.create_ctrl()
            control.color_ctrl()
            control_obj.setTranslation(flc_tra)

            # create joint
            jnt_ribbon_name = 'jnt_{}_{:03d}'.format(self.ribbon_name, pad)
            jnt_ribbon = pm.joint(name = jnt_ribbon_name)

            # parent joint to control to srt_buf
            pm.parent(control_obj, flc)
            sb.srt_buf([control_obj])


    def add_sine(self):

        nurbs_sine = pm.duplicate(self.nurbs, name = 'geo_' + self.ribbon_name + '_sine')

        # create sine deformer
        dfm_sine, tfm_sine = pm.nonLinear(nurbs_sine, type = 'sine')
        tfm_sine.setRotation([0, 0, 90], space = 'world')
        dfm_sine.dropoff.set(1)

        pm.blendShape(nurbs_sine, self.nurbs, weight = [0, 1])


    def match_jnt(self, jnt_A, jnt_B):

        jnt_ribbon_A_pos = [-self.ribbon_segment / 2.0, 0, 0]
        jnt_ribbon_B_pos = [self.ribbon_segment / 2.0, 0, 0]

        pm.select(clear = True)
        jnt_ribbon_A = pm.joint(position = jnt_ribbon_A_pos, name = 'jnt_' + self.ribbon_name + '_A')
        jnt_ribbon_A.deselect()
        jnt_ribbon_B = pm.joint(position = jnt_ribbon_B_pos, name = 'jnt_' + self.ribbon_name + '_B')
        jnt_ribbon_B.deselect()


        buf_jnt_ribbon_A, srt_jnt_ribbon_A = sb.srt_buf([jnt_ribbon_A])
        buf_jnt_ribbon_B, srt_jnt_ribbon_B = sb.srt_buf([jnt_ribbon_B])

        pm.skinCluster(jnt_ribbon_A, jnt_ribbon_B, self.nurbs, name = 'skc_' + self.ribbon_name)

        pm.aimConstraint(jnt_ribbon_B, jnt_ribbon_A, aim = [1, 0, 0], upVector = [1, 0, 0], worldUpVector = [1, 0, 0], worldUpObject = jnt_A)
        pm.aimConstraint(jnt_ribbon_A, jnt_ribbon_B, aim = [-1,0, 0], upVector = [1, 0, 0], worldUpVector = [1, 0, 0], worldUpObject = jnt_A)

        pm.parentConstraint(jnt_A, srt_jnt_ribbon_A, mo = False)
        pm.parentConstraint(jnt_B, srt_jnt_ribbon_B, mo = False)



selected = pm.ls(os = True)
ribbon = CreateRibbon('ribbon_01', 4)
ribbon.create_nurbs()
ribbon.add_flc()
ribbon.add_ctrl_jnt()
ribbon.add_sine()
ribbon.match_jnt(selected[0], selected[1])