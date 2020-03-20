'''
FK Chain Parent Constraint Tool
Ussually FK control children are parented to their control parents,
however, Phillip Kauffold, Game Technical Art Instructor,
suggested the separation of each controls.
'''

import pymel.core as pm

selection = pm.ls(os=True)

def parent_scale_cnst(parent, child, maintain_ofs=True):
    # pm.parent(child, parent)
    pm.parentConstraint(parent, child, mo=maintain_ofs)
    pm.scaleConstraint(parent, child)

def cnst_chain(selection):
    '''
    constraint a chain of controls with srt transform.

    Just select the top most parent,
    to the lowest child.
    '''
    for parent, child in zip(selection, selection[1:]):
        child_srt = pm.listRelatives(child, parent=True)
        # child_cst = pm.listRelatives(child_srt, parent=True)
        parent_scale_cnst(parent, child_srt, maintain_ofs=True)

def cnst_pair(selection):
    '''
    constraint a set of controls to a set of corresponding joints.

    Just select parents,
    then children.
    the amount of parents must equal children.
    '''
    n_sel = len(selection)
    half_n_sel = n_sel // 2

    for parent, child in zip(selection[:half_n_sel], selection[half_n_sel:]):
        parent_scale_cnst(parent, child, maintain_ofs=True)

def cnst_main(selection):
    '''
    constraint a set of controls to a single main control

    just select the main parent,
    then all of the child.
    '''
    ctrl_main = selection[0]
    children = selection[1:]

    for child in children:
        child_srt = pm.listRelatives(child, parent=True)
        parent_scale_cnst(ctrl_main, child_srt, maintain_ofs=True)

cnst_chain(selection)