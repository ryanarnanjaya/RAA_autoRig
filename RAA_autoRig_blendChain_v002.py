'''
Blends FK IK chains to an output chain
blend from 0 to 10
'''

import pymel.core as pm

def blend_chain(FK_chain_list, IK_chain_list, output_chain_list, ctrl, translate = True, rotate = True, scale = True):

    # create chainBlend attr for ctrl
    ctrl.addAttr('FKIK', niceName = "FK IK", shortName = "fkik", attributeType = 'float',
                 defaultValue = 0, maxValue = 1, minValue = 0, keyable = True, hidden = False)

    # for every output in output_chain_list
    for FK, IK, output in zip(FK_chain_list, IK_chain_list, output_chain_list):
        print(FK, IK, output)
        if translate or rotate:
            pair_blend = pm.createNode('pairBlend')
            ctrl.FKIK >> pair_blend.weight

        if translate:
            FK.translate >> pair_blend.inTranslate1
            IK.translate >> pair_blend.inTranslate2
            pair_blend.outTranslate >> output.translate

        if rotate:
            FK.rotate >> pair_blend.inRotate1
            IK.rotate >> pair_blend.inRotate2
            pair_blend.outRotate >> output.rotate

        if scale:
            blend_colors = pm.createNode('blendColors')
            # connect attributes
            FK.scale >> blend_colors.color2
            IK.scale >> blend_colors.color1
            blend_colors.output >> output.scale
            ctrl.FKIK >> blend_colors.blender

sel = pm.ls(os=True)
# blend_chain(sel[:3], sel[3:6], sel[6:9], sel[9])
def proxy_attr(source_attr, output, output_long_name, output_nice_name):
    for obj in output:
        pm.addAttr(obj, longName=output_long_name, niceName=output_nice_name, proxy=source_attr)
attr = sel[0].FKIK
proxy_attr(attr, sel[1:], 'FKIK', 'FK IK')