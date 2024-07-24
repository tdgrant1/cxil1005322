""" These are all the relevant global configurations for the experiment analysis """
from reborn import detector, source
from reborn.detector import epix100_pad_geometry_list, PADGeometryList
from reborn.external.crystfel import geometry_file_to_pad_geometry_list
import numpy as np

def default_config(detector='jungfrau'):
    r""" Create the default configurations.  You should not use this directly; instead use
    get_config which should provide run-specific parameters. 
    detector = jungfrau by default, alternatively epix.
    """
    # general configurations
    # required keys: experiment_id
    # possible keys: results_directory, cachedir
    config = dict(experiment_id='cxil1005322',
                  results_directory='results',
                  hdf5_directory="/sdf/data/lcls/ds/cxi/cxil1005322/results/cxil1005322/hdf5/",
                  cachedir='cache/',
                  debug=1,
                  joblib_directory="results/joblib",
                  photon_wavelength_pv='SIOC:SYS0:ML00:AO192')
    # detector configurations (we make a dictionary for every available PAD detector)
    # required keys: pad_id, geometry
    # possible keys: mask, motions
    # NOTES -- geometry: can be path to geom file or a pad_geometry_list_object
    #              mask: list of paths to masks (you can use multiple masks to take care of one particular feature)
    #                    example: ['badrows.mask', 'edges.mask', 'spots.mask', 'threshold.mask']
    #           motions: dictionary
    #                    example: {'epics_pv':'CXI:DS1:MMS:06.RBV', 'vector':[0, 0, 1e-3]}

    #jungfrau_geometry_file = './geometry/jungfrau4M_AgBeh.json'
    jungfrau_geometry_file = './geometry/tom_agbe_run7_fitellipse_fixdistance.json'
    jungfrau_masks = [
    # "geometry/edge_mask.mask",
    # "geometry/jungfrau_edges_belowstd-outer_abovestd-inner.mask",
    # "geometry/jungfrau_dark_spot.mask",
    ]
    jungfrau4m = dict(pad_id='jungfrau4M',
                      geometry=PADGeometryList(filepath=jungfrau_geometry_file),
                      data_type='calib',
                      mask=jungfrau_masks,
                      )

    epix_geometry_file = './geometry/epix_recentered_postmove_r163.json'
    epix_masks = [
    "geometry/epix_edges.mask",
    ]
    epix10ka_1 = dict(pad_id='epix10ka_1',
                      geometry=PADGeometryList(filepath=epix_geometry_file),
                      data_type='calib',
                      mask=epix_masks,
                      )
    # epix100 = dict(pad_id='epix100',
    #                geometry=epix100_pad_geometry_list(detector_distance=1),
    #                data_type='raw')

    #best not to do both detectors at the same time
    if detector == "jungfrau":
        config['pad_detectors'] = [jungfrau4m]  # list allows for multiple detectors
    elif detector == "epix":
        config['pad_detectors'] = [epix10ka_1]
    else:
        print(f"ERROR: {detector} detector unknown. Either jungfrau or epix.")

    # radial profiler configurations
    config['profiles'] = dict(n_bins=500,
                              q_range=[0, 3e10])
    # runstats configurations
    histogram_config = dict(bin_min=-5, bin_max=50, n_bins=100, zero_photon_peak=0, one_photon_peak=8)
    runstats_config = dict(log_file=None,
                           checkpoint_file=None,
                           checkpoint_interval=250,
                           message_prefix='',
                           debug=False,
                           histogram_params=histogram_config)
    config['runstats'] = runstats_config
    pvs = {"photonBeam_rate": "EVNT:SYS0:1:LCLSBEAMRATE",
           "photonBeam_wavelength": "SIOC:SYS0:ML00:AO192",
           "photonBeam_energy": "SIOC:SYS0:ML00:AO627",
           "photonBeam_pulse_energy": "SIOC:SYS0:ML00:AO541",
           "eBeam_pulse_length": "SIOC:SYS0:ML00:AO820",
           "Acqiris": "CxiEndstation.0:Acqiris.0"}
    config["pvs"] = pvs
    config["beam"] = source.load_beam("geometry/beam.json")
    return config


base_config = default_config


# Run-specific modifications go here, e.g. if you want to manually set the
# geometry for a set of runs.
def get_config(run_number, detector="jungfrau"):
    # This is the place to modify the config according to run number (e.g. detector geometry, etc.)
    config = default_config(detector)
    run = f"r{run_number:04d}"
    results = config['results_directory'] + '/runstats/' + run + '/'  # e.g. ./results/runstats/r0045/
    # results = 'results/runstats/' + run + '/'  # e.g. ./results/runstats/r0045/
    # config['runstats']['results_directory'] = results
    config['run_number'] = run_number
    config['runstats']['checkpoint_file'] = results + "checkpoints/" + run
    config['runstats']['log_file'] = results + "logs/" + run 
    if detector == "jungfrau":
        if run_number in range(12,19):
            config['pad_detectors'][0]['mask'].append('geometry/rebecca_run12-18.mask')
        elif run_number in range(21,26):
            config['pad_detectors'][0]['mask'].append('geometry/samantha_run21-25.mask')
        elif run_number in range(27,30):
            config['pad_detectors'][0]['mask'].append('geometry/rebecca_run27-29.mask')
        elif run_number in range(30,33):
            config['pad_detectors'][0]['mask'].append('geometry/rebecca_run30-32.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_r32_weird_min_pixels.mask')
        elif run_number in range(37,48):
            config['pad_detectors'][0]['mask'].append('geometry/nelly_run37-47.mask')
        elif run_number in range(49,52):
            config['pad_detectors'][0]['mask'].append('geometry/nelly_run49-51.mask')
        elif run_number in range(53,66):
            config['pad_detectors'][0]['mask'].append('geometry/nelly_run53-65.mask')
        elif run_number in range(56,69):
            config['pad_detectors'][0]['mask'].append('geometry/nelly_run66-68.mask')
        elif run_number in range(72,78):
            config['pad_detectors'][0]['mask'].append('geometry/nelly_run72-77.mask')
        elif run_number in range(79,82):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run79-81.mask')
        elif run_number in range(83,85):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run83-84.mask')
        elif run_number == 86:
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run86.mask')
        elif run_number in range(87,91):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run87-90.mask')
        elif run_number == 91:
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run91.mask')
        elif run_number in range(82,95):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run92-94.mask')
        elif run_number in range(96,99):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run96-98.mask')
        elif run_number in range(99,103):
            config['pad_detectors'][0]['mask'].append('geometry/felicity_run99-102.mask')
        elif run_number in range(106,121):
            config['pad_detectors'][0]['mask'].append('geometry/melody_run106-120.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run106-120.mask')
        elif run_number in range(122,125):
            config['pad_detectors'][0]['mask'].append('geometry/kaya_run122-124.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run122-124.mask')
        elif run_number in range(125,128):
            config['pad_detectors'][0]['mask'].append('geometry/kaya_run125-127.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run125-127.mask')
        elif run_number in range(128,135):
            config['pad_detectors'][0]['mask'].append('geometry/kaya_run128-134.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run128-134.mask')
        elif run_number in range(135,140):
            config['pad_detectors'][0]['mask'].append('geometry/kaya_run135-139.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run135-139.mask')
        elif run_number in range(141,144):
            config['pad_detectors'][0]['mask'].append('geometry/samantha_run141-143.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run141-143.mask')
        elif run_number in range(145,147):
            config['pad_detectors'][0]['mask'].append('geometry/samantha_run145-146.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run144-146.mask')
        elif run_number in range(149,156):
            config['pad_detectors'][0]['mask'].append('geometry/samantha_run149-155.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run149-155.mask')
        elif run_number in range(156,159):
            config['pad_detectors'][0]['mask'].append('geometry/samantha_run156-158.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run156-158.mask')
        elif run_number in range(168,175):
            config['pad_detectors'][0]['mask'].append('geometry/elizabeth_run168-174.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run168-174.mask')
        elif run_number in range(176,187):
            config['pad_detectors'][0]['mask'].append('geometry/elizabeth_run176-186.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run176-186.mask')
        elif run_number in range(187,194):
            config['pad_detectors'][0]['mask'].append('geometry/elizabeth_run187-193.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run187-193.mask')
        elif run_number in range(197,205):
            config['pad_detectors'][0]['mask'].append('geometry/kirsten_run197-204.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run197-204.mask')
        elif run_number in range(205,218):
            config['pad_detectors'][0]['mask'].append('geometry/kirsten_run205-217.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run205-217.mask')
        elif run_number in range(222,224):
            config['pad_detectors'][0]['mask'].append('geometry/kirsten_run222-223.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run222-223.mask')
        elif run_number in range(227,234):
            config['pad_detectors'][0]['mask'].append('geometry/cecile_run227-233.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run227-233.mask')
        elif run_number in range(235,252):
            config['pad_detectors'][0]['mask'].append('geometry/cecile_run235-251.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run235-251.mask')
        elif run_number in range(255,263):
            config['pad_detectors'][0]['mask'].append('geometry/maryellen_run255-262.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run255-262.mask')
        elif run_number in range(263,266):
            config['pad_detectors'][0]['mask'].append('geometry/maryellen_run263-265.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run263-265.mask')
        elif run_number in range(266,274):
            config['pad_detectors'][0]['mask'].append('geometry/maryellen_run266-273.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run266-273.mask')
        elif run_number in range(274,282):
            config['pad_detectors'][0]['mask'].append('geometry/maryellen_run274-281.mask')
            config['pad_detectors'][0]['mask'].append('geometry/jungfrau_diode_mask_run274-281.mask')
    config['runstats']['message_prefix'] = f"Run {run_number}: "
    return config


def get_geometry(run_number=None):
    # our convention is for the primary (saxs in this experiment) detector to be first in the list
    c = get_config(run_number=run_number)
    pads = c['pad_detectors'][0]['geometry']
    if isinstance(pads, str):
        return detector.load_pad_geometry_list(pads)
    elif isinstance(pads, detector.PADGeometryList):
        return pads
    else:
        print('The geometry is not understood, please review the config file.')


if __name__ == '__main__':
    print(f'Base Configurations:\n\t{base_config()}')
