'''
colors
shape
'''
import pymel.all as pm



class CreateCtrl:

    triangle = 'triangle'
    square = 'square'
    octagon = 'octagon'
    circle = 'circle'
    cube = 'cube'
    pyramid = 'pyramid'
    cone = 'cone'
    diamond = 'diamond'
    one_arrow = 'one_arrow'
    two_arrow = 'two_arrow'
    two_arrow_curved = 'two_arrow_curved'
    four_arrow = 'four_arrow'
    ring = 'ring'
    sun = 'sun'

    def __init__(self, name, side, shape, color):
        self.shape = shape
        # use color index
        self.color = color
        # R,M,L for Right, Middle, Left
        self.side = side

        self.name = name



    def create_ctrl(self):

        if self.shape == CreateCtrl.triangle:
            ctrl = pm.curve(name = self.name, d=1, p=[(-1,0,1),(1,0,1),(0,0,-1),(-1,0,1)], k=[0,1,2,3,])

        elif self.shape == CreateCtrl.square:
            ctrl = pm.curve(name = self.name, degree = 1,
                               point = [(0, 2, 2), (0, 2, -2), (0, -2, -2), (0, -2, 2), (0, 2, 2)])

        elif self.shape == CreateCtrl.octagon:
            ctrl = pm.curve(name = self.name, degree = 1,
                               point = [(0, 3, 1), (0, 3, -1), (0, 1, -3), (0, -1, -3), (0, -3, -1), (0, -3, 1), (0, -1, 3), (0, 1, 3), (0, 3, 1)])

        elif self.shape == CreateCtrl.circle:
            ctrl = pm.circle(name = self.name, normalX = 1, normalZ = 0, radius = 2, constructionHistory = False)[0]

        elif self.shape == CreateCtrl.cube:
            ctrl = pm.curve(name = self.name, degree = 1,
                               point = [(1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1),
                                        (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, -1, 1),
                                        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1)])

        elif self.shape == CreateCtrl.pyramid:
            ctrl = pm.curve(name = self.name, degree = 1,
                               point = [(1, 2, 1), (1, 2, -1), (-1, 2, -1), (-1, 2, 1), (1, 2, 1), (0, 0, 0),
                                        (1, 2, -1), (-1, 2, -1), (0, 0, 0), (-1, 2, 1)])
        elif self.shape == CreateCtrl.cone:
            ctrl = pm.curve(name = self.name, d=1, p=[(-0.5, 2, 0.866025),(0, 0, 0),(0.5, 2, 0.866025),(-0.5, 2, 0.866025),(-1, 2, -1.5885e-07),
                                                      (0, 0, 0),(-1, 2, -1.5885e-07),(-0.5, 2, -0.866026),(0, 0, 0),(0.5, 2, -0.866025),
                                                      (-0.5, 2, -0.866026),(0.5, 2, -0.866025),(0, 0, 0),(1, 2, 0), (0.5, 2, -0.866025),
                                                      (1, 2, 0),(0.5, 2, 0.866025)  ], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])

        elif self.shape == CreateCtrl.diamond:
            ctrl = pm.curve(name = self.name, degree = 1,
                               point = [(1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1), (1, 0, 1), (0, -2, 0),
                                        (1, 0, -1), (-1, 0, -1), (0, -2, 0), (-1, 0, 1),
                                        (1, 0, 1), (0, 2, 0),
                                        (1, 0, -1), (-1, 0, -1), (0, 2, 0), (-1, 0, 1)])

        elif self.shape == CreateCtrl.one_arrow:
            ctrl = pm.curve(name = self.name, d=1, p=[(0, 1.003235, 0),(0.668823, 0, 0),(0.334412, 0, 0),(0.334412, -0.167206, 0),(0.334412, -0.501617, 0),(0.334412, -1.003235, 0),(-0.334412, -1.003235, 0),(-0.334412, -0.501617, 0),(-0.334412, -0.167206, 0),(-0.334412, 0, 0),(-0.668823, 0, 0),(0, 1.003235, 0)], k=[0,1,2,3,4,5,6,7,8,9,10,11])

        elif self.shape == CreateCtrl.two_arrow:
            ctrl = pm.curve(name = self.name, d=1, p=[(0, 1, 0),(1, 1, 0),(2, 1, 0),(3, 1, 0),(3, 2, 0),(4, 1, 0),(5, 0, 0),(4, -1, 0),(3, -2, 0),(3, -1, 0),(2, -1, 0),(1, -1, 0),(0, -1, 0),(-1, -1, 0),(-2, -1, 0),(-3, -1, 0),(-3, -2, 0),(-4, -1, 0),(-5, 0, 0),(-4, 1, 0),(-3, 2, 0),(-3, 1, 0),(-2, 1, 0),(-1, 1, 0),(0, 1, 0),], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])

        elif self.shape == CreateCtrl.two_arrow_curved:
            ctrl = pm.curve(name = self.name, d=1, p=[(-0.251045, 0, -1.015808), (-0.761834, 0, -0.979696), (-0.486547, 0, -0.930468), (-0.570736, 0, -0.886448), (-0.72786, 0, -0.774834), (-0.909301, 0, -0.550655), (-1.023899, 0, -0.285854), (-1.063053, 0, 9.80765e-009), (-1.023899, 0, 0.285854), (-0.909301, 0, 0.550655), (-0.72786, 0, 0.774834), (-0.570736, 0, 0.886448), (-0.486547, 0, 0.930468), (-0.761834, 0, 0.979696), (-0.251045, 0, 1.015808), (-0.498915, 0, 0.567734), (-0.440202, 0, 0.841857), (-0.516355, 0, 0.802034), (-0.658578, 0, 0.701014), (-0.822676, 0, 0.498232), (-0.926399, 0, 0.258619), (-0.961797, 0, 8.87346e-009), (-0.926399, 0, -0.258619), (-0.822676, 0, -0.498232), (-0.658578, 0, -0.701014), (-0.516355, 0, -0.802034), (-0.440202, 0, -0.841857), (-0.498915, 0, -0.567734), (-0.251045, 0, -1.015808)], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28])

        elif self.shape == CreateCtrl.four_arrow:
            ctrl = pm.curve(name = self.name, d=1, p=[(1, 0, 1),(3, 0, 1),(3, 0, 2),(5, 0, 0),(3, 0, -2),(3, 0, -1),(1, 0, -1),(1, 0, -3),(2, 0, -3),(0, 0, -5),(-2, 0, -3),(-1, 0, -3),(-1, 0, -1),(-3, 0, -1),(-3, 0, -2),(-5, 0, 0),(-3, 0, 2),(-3, 0, 1),(-1, 0, 1),(-1, 0, 3),(-2, 0, 3),(0, 0, 5),( 2, 0, 3),(1, 0, 3),(1, 0, 1),], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])

        elif self.shape == CreateCtrl.ring:
            ctrl = pm.curve(name = self.name, d=1, p=[(-0.707107, 0.0916408, 0.707107),(0, 0.0916408, 1), (0, -0.0916408, 1), (-0.707107, -0.0916408, 0.707107), (-0.707107, 0.0916408, 0.707107),(-1, 0.0916408, 0), (-1, -0.0916408, 0), (-0.707107, -0.0916408, 0.707107), (-1, -0.0916408, 0), (-0.707107, -0.0916408, -0.707107), (-0.707107, 0.0916408, -0.707107), (-1, 0.0916408, 0), (-0.707107, 0.0916408, -0.707107), (0, 0.0916408, -1), (0, -0.0916408, -1), (-0.707107, -0.0916408, -0.707107),(-0.707107, 0.0916408, -0.707107), (-0.707107, -0.0916408, -0.707107), (0, -0.0916408, -1), (0.707107, -0.0916408, -0.707107), (0.707107, 0.0916408, -0.707107), (0, 0.0916408, -1), (0.707107, 0.0916408, -0.707107), (1, 0.0916408, 0), (1, -0.0916408, 0), (0.707107, -0.0916408, -0.707107), (1, -0.0916408, 0), (0.707107, -0.0916408, 0.707107), (0.707107, 0.0916408, 0.707107), (1, 0.0916408, 0), (0.707107, 0.0916408, 0.707107),(0, 0.0916408, 1), (0, -0.0916408, 1), (0.707107, -0.0916408, 0.707107)], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33])

        elif self.shape == CreateCtrl.sun:
            ctrl = pm.circle(name = self.name, s=16, nr=[0,1,0])[0]
            pm.select((ctrl + '.cv[1]'), (ctrl + '.cv[3]'), (ctrl + '.cv[5]'), (ctrl + '.cv[7]'), (ctrl + '.cv[9]'), (ctrl + '.cv[11]'), (ctrl + '.cv[13]'), (ctrl + '.cv[15]'), (ctrl + '.cv[17]'), (ctrl + '.cv[19]'), r=True)
            pm.scale(0.3, 0.3, 0.3, p=[0, 0, 0], r=True)
            pm.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
            pm.xform(ctrl, cp=True)

        print(ctrl)
        self.obj = ctrl
        return self.obj

    def color_ctrl(self):
        self.obj.overrideEnabled.set(1)
        self.obj.overrideColor.set(self.color)
        return self.color
# option 1
# ctrl_list = [CreateCtrl('ctrl_shoulder_L', 'L', 'cone', 7), CreateCtrl('ctrl_arm_R', 'R', 'pyramid', 4)]
# ctrl_shoulder_L, ctrl_arm_R = ctrl_list

# option 2 is clearer
# ctrl_shoulder_L = CreateCtrl('ctrl_shoulder_L', 'L', 'cone', 7)
# ctrl_arm_R = CreateCtrl('ctrl_arm_R', 'R', 'pyramid', 4)

# ctrl_list = [ctrl_shoulder_L, ctrl_arm_R]

# for instance in ctrl_list:
#     instance.create_ctrl()
#     instance.color_ctrl()

# ctrl = CreateCtrl('ctrl_triangle', 'L', 'ring', 7)
# ctrl.create_ctrl()
# ctrl.color_ctrl()