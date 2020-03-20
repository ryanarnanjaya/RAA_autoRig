'''
Create new offset groups
'''
import pymel.core as pm


def move(target, child, space = 'world'):
    if space == 'world':
        target_matrix = target.getMatrix(worldSpace = True)
        child.setMatrix(target_matrix, worldSpace = True)
    if space == 'object':
        target_matrix = target.getMatrix(objectSpace = True)
        child.setMatrix(target_matrix, objectSpace = True)
    return target_matrix

def srt_buf(selection):
    for obj in selection:
        obj_parent = obj.listRelatives(parent = True)
        obj_children = obj.listRelatives(children = True)
        if obj_parent:
            pm.parent(obj, world = True)
        if len(obj_children) > 1:
            pm.parent(obj_children[1:], world = True)

        pm.makeIdentity(obj, apply = True, scale = True,)

        # get obj name
        obj_name = obj.name(long = None)

        # define group names
        buf_grp_name = 'buf_' + obj_name
        srt_grp_name = 'srt_' + obj_name
        # cpy_grp_name = 'cpy_' + obj_name

        # create groups
        buf_grp = pm.group(name = buf_grp_name, empty = True)
        srt_grp = pm.group(name = srt_grp_name, empty = True)

        for grp in [buf_grp, srt_grp]:
            obj_matrix = move(obj, grp, 'world')
        pm.parent(obj, srt_grp)
        pm.parent(srt_grp, buf_grp)

        # cpy_grp = pm.group(name = cpy_grp_name, empty = True, parent = srt_grp)

        # connect obj attributes to cpy_grp
        # obj.translate >> cpy_grp.translate
        # obj.rotate >> cpy_grp.rotate
        # obj.scale >> cpy_grp.sfcale

        # parent groups back to the hierarchy, if list is not empty
        if obj_parent:
            pm.parent(buf_grp, obj_parent[0])
        if len(obj_children) > 1:
            pm.parent(obj_children[1:], obj)

    return buf_grp, srt_grp

# selected = pm.ls(os = True)
# print(srt_buf(selected))
