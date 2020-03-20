'''
match a control xform to a joint
first select a joint, then the control
'''
import pymel.all as pm

def match_ctrl(jnt, ctrl):
    control_name = ctrl.name(long = None)
    control_shape = ctrl.getShape()

    transform = pm.group(parent = jnt, empty = True)
    transform.zeroTransformPivots()
    pm.parent(transform, world = True)

    pm.parent(control_shape, transform, absolute = True, shape = True)

    new_trans = pm.listRelatives(control_shape, parent = True)

    pm.makeIdentity(new_trans, s = True, r = True, t = True, apply = True)

    pm.parent(control_shape, transform, relative = True, shape = True)

    pm.delete(new_trans, ctrl)

    transform.rename(control_name)

    pm.delete(transform, constructionHistory = True)

sel = pm.ls(os=True)
match_ctrl(sel[0], sel[1])