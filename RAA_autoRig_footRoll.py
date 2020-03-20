'''
Foot Roll Script
'''
'''
Selection
total 7

4 foot roll joints:
    heel
    toe
    ball
    ankle

2 foot IK joints:
    ankle
    ball

1 IK control
'''
'''
IK control Attributes
total 6

roll
ankle

heelTwist
toeTwist
ankleTwist

ankleLR
'''

import pymel.core as pm

selection = pm.ls(os=True)

def add_attr_divider(obj):
    '''
    add a divider attribute for channel box
    '''
    attr = '__________'
    while pm.attributeQuery(attr, node=obj, exists=True):
        attr += '_'
    else:
        obj.addAttr(attr, niceName='..................................................................................',
                    attributeType='enum', defaultValue=0, keyable=False, hidden=False,
                    enumName='..................................................................................')
        obj.setAttr(attr, channelBox=True)

def foot_roll():
    jnt_rev = selection[:4]
    jnt_IK = selection[4:6]
    ctrl_IK = selection[6]

    # create attributes and dividers
    add_attr_divider(ctrl_IK)
    ctrl_IK.addAttr('roll', niceName='Roll', shortName='rl', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)
    ctrl_IK.addAttr('ankle', niceName='Ankle', shortName='akl', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)

    add_attr_divider(ctrl_IK)
    ctrl_IK.addAttr('heelTwist', niceName='Heel Twist', shortName='htw', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)
    ctrl_IK.addAttr('toeTwist',niceName='Toe Twist', shortName='ttw', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)
    ctrl_IK.addAttr('ankleTwist', niceName='Ankle Twist', shortName='atw', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)

    add_attr_divider(ctrl_IK)
    ctrl_IK.addAttr('ankleLR', niceName='Ankle LR', shortName='alr', attributeType='float', defaultValue=0,
                    keyable=True, hidden=False)

    # connect attributes
    ctrl_IK.roll >> jnt_rev[0].rx
    ctrl_IK.roll >> jnt_rev[1].rx
    ctrl_IK.ankle >> jnt_rev[2].rx

    ctrl_IK.heelTwist >> jnt_rev[0].ry
    ctrl_IK.toeTwist >> jnt_rev[1].ry
    ctrl_IK.ankleTwist >> jnt_rev[2].ry

    ctrl_IK.ankleLR >> jnt_rev[2].rz

    # set jnt_rev limits
    # jnt_rev[0].maxRotLimitEnable.maxRotXLimitEnable.set(1)
    # jnt_rev[0].maxRotLimit.maxRotXLimit.set(0)
    pm.transformLimits(jnt_rev[0], erx=[False, True], rx=[0,0])
    pm.transformLimits(jnt_rev[1], erx=[True, False], rx=[0,0])

    # orient constraint jnt_IK to jnt_rev
    pm.orientConstraint(jnt_rev[1], jnt_IK[1], mo=True)
    pm.orientConstraint(jnt_rev[2], jnt_IK[0], mo=True)

foot_roll()