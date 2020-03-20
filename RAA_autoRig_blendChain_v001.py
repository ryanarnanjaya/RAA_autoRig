'''
Blends FK IK chains to an output chain
'''

import pymel.core as pm

def blend_chain(FK_chain_list, IK_chain_list, output_chain_list, ctrl, translate = True, rotate = True, scale = True):

    # create chainBlend attr for ctrl
    ctrl.addAttr('FKIK', niceName = "FK IK", shortName = "fkik", attributeType = 'float',
                 defaultValue = 0, maxValue = 1, minValue = 0, keyable = True, hidden = False)

    # attribute list based on cnst parameters
    attr_list = []

    if translate:
        attr_list.append('translate')

    if rotate:
        attr_list.append('rotate')

    if scale:
        attr_list.append('scale')

    # create an empty blend colors list
    blend_colors_list = []

    # for every output in output_chain_list
    for FK, IK, output in zip(FK_chain_list, IK_chain_list, output_chain_list):

        # for every chosen attribute in attr_list
        for attr_name in attr_list:

            blend_colors   = pm.createNode('blendColors')
            blend_colors_list.append(blend_colors)

            FK_attr = FK.attr(attr_name)
            IK_attr = IK.attr(attr_name)

            output_attr = output.attr(attr_name)
            blend_attr_1 = blend_colors.color1
            blend_attr_2 = blend_colors.color2

            # connect attributes
            FK_attr >> blend_attr_2
            IK_attr >> blend_attr_1

            blend_colors.output >> output_attr

    # for every blend colors node in blend_colors_list
    for node in blend_colors_list:

        ctrl.FKIK >> node.blender

# selected = pm.ls(os = True)
# blend_chain(selected[:2], selected[3:5], selected[6:8], selected[9])