#!/usr/bin/env python
import argparse
import numpy as np
#from framegetter import LY59FrameGetterV2, LY59FrameGetterV4
from reborn.external.lcls import LCLSFrameGetter
from reborn.viewers.qtviews import PADView
from config import get_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run_number', type=int, default=131, help='Run number')
    parser.add_argument('--h5', action="store_true", default=False, help="Use converted data.")
    parser.add_argument('--h5v4', action="store_true", default=False, help="Use converted data.")
    parser.add_argument('--streakmask', action="store_true", default=False, help="Look up pre-made streak masks")
    parser.add_argument('--raw', action="store_true", default=False, help="Use raw data, default is calib.")
    args = parser.parse_args()
    config = get_config(run_number=args.run_number)

    data_type = 'raw' if args.raw else 'calib'

#    if args.h5:
#        fg = LY59FrameGetterV2(run_number=args.run_number,
#                             data_type=data_type)
#    elif args.h5v4:
#        if args.streakmask is True:
#            streakmask = f"/sdf/data/lcls/ds/cxi/cxily5921/scratch/data/v4/streakmasks/r{args.run_number:04d}/streakmasks.h5"
#            print("Using streakmask", streakmask)
#        else:
#            streakmask = None
#        fg = LY59FrameGetterV4(run_number=args.run_number,
#                             data_type=data_type, streakmask=streakmask)
#    else:
    if True:
        for pad_dict in config['pad_detectors']:
            pad_dict['data_type'] = data_type
        fg = LCLSFrameGetter(experiment_id=config['experiment_id'],
                             run_number=args.run_number,
                             pad_detectors=config['pad_detectors'],
                             cachedir=config['cachedir'],
                             photon_wavelength_pv=config["photon_wavelength_pv"])
    pv = PADView(frame_getter=fg,
                 debug_level=1,
                 levels=(0, 7),)
    #             post_processors=[lambda x: np.log(x)])
    pv.set_mask_color([128, 0, 0, 75])
    pv.start()
