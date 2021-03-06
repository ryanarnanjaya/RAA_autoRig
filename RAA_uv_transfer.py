'''
Utility for transfering UV from a similar base mesh to a rigged base mesh.
Originally Written using Python by Ryan Arnanjaya.
Rewritten using PyMel by Ryan Arnanjaya.

Instruction:
Select object with desired UV,
then select destination object.
'''

import pymel.core as pm
import logging

logger = logging.getLogger(__name__)


def uv_transfer():
    selection = pm.ls(os=True)
    if len(selection) == 2:
        obj_uv = selection[0]
        obj_destination = selection[1]
        relative = pm.listRelatives(obj_destination, children=True)
        logging.debug(relative)
        # get intermediate obj in relative.
        intermediate = pm.ls(relative, intermediateObjects=True)
        logging.debug(intermediate)
        len_inter = len(intermediate)
        logging.debug('Found {} intermediate objects.'.format(len_inter))
        for shape_orig in intermediate:
            shape_orig.intermediateObject.set(0)
            pm.transferAttributes(obj_uv, shape_orig, transferPositions=0,
                                  transferNormals=0, transferUVs=2,
                                  transferColors=0, sampleSpace=5,
                                  searchMethod=3, flipUVs=0,
                                  colorBorders=1)
            logging.info('UVs transfered.')
            pm.delete(shape_orig, ch=True)
            shape_orig.intermediateObject.set(1)
            logging.info('Operation successful.')

    else:
        # must select 2 objects.
        msg = 'Select object with UV, then select destination object.'
        raise Exception(msg)


uv_transfer()
