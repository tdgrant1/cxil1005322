#!/usr/bin/env python
import argparse
import numpy as np
import pyqtgraph as pg
import joblib
from reborn.external.pyqtgraph import imview
from reborn.external.lcls import LCLSFrameGetter
from reborn import analysis
import config
import reborn
import os

default_config = config.default_config()
memory = joblib.Memory(default_config["joblib_directory"])

# class MyParallelRadialProfiler(analysis.saxs.ParallelRadialProfiler):
#     def __init__(self,**kwargs):
#         r"""
#         Modifies the standard ParallelRadialProfiler to allow additional entries into the dict
#         """
#         super().__init__(framegetter=framegetter, **kwargs)

#         #add some entries to the dictionary for my pv values I want to save
#         self.radials["Acqiris"] = []

#     #writing my own add_frame to add in the pv values to the dict
#     #copy the original add_frame() method, but then add some lines to it
#     def add_frame(self, dat: DataFrame):
#         print(dat.keys())
#         if dat.validate():
#             #data = dat.get_raw_data_flat()
#             data = dat.get_processed_data_flat()
#             mask = dat.get_mask_flat()
#             if self.sap is None:
#                 g = dat.get_pad_geometry()
#                 b = dat.get_beam()
#                 self.sap = g.polarization_factors(beam=b)*g.solid_angles()
#             weights= self.sap*mask
#             out = self.profiler.quickstats(data=data, weights=weights)
#             self.radials["sum"].append(out["sum"])
#             self.radials["sum2"].append(out["sum2"])
#             self.radials["wsum"].append(out["weight_sum"])
#             self.radials["mean"].append(out["mean"])
#             self.radials["sdev"].append(out["sdev"])
#             self.radials["frame_id"].append(dat.get_frame_id())
#             self.radials["n_frames"] += 1
#             if self.kwargs["include_median"]:
#                 m = self.profiler.get_median_profile(data=data, mask=mask)
#                 self.radials["median"].append(m)

#             #my additions:
#             self.radials["Acqiris"].append(data)

@memory.cache(ignore=["n_processes"])
def get_radials(run_number=1, n_processes=1, start=0, stop=None, detector="jungfrau"):
    max_events = 1e7
    conf = config.get_config(run_number, detector)
    log_file = os.path.dirname(conf["runstats"]["log_file"])
    if not os.path.isdir(log_file):
        if not os.path.isdir(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        os.mkdir(log_file)
    RUNNING_file = log_file + "/RUNNING"
    with open(RUNNING_file, 'w') as f:
        f.close()
    runstats_conf = conf["runstats"]
    if stop is None:
        runstats_conf["stop"] = max_events
    else:
        runstats_conf["stop"] = stop
    runstats_conf["start"] = start
    runstats_conf["n_processes"] = n_processes
    detectors = conf["pad_detectors"]
    for d in detectors:
        d["mask"] = None
    framegetter = LCLSFrameGetter(
        run_number=run_number,
        max_events=max_events,
        experiment_id=conf["experiment_id"],
        pad_detectors=detectors,
        cachedir=conf["cachedir"],
        postprocessors=None,
        photon_wavelength_pv=conf["photon_wavelength_pv"]
    )
    #remove histogram parameters from dictionary
    del runstats_conf["histogram_params"]
    #ParallelRadialProfiler does not appear to retrieve the geometry, beam, masks from
    #the framegetter (though it probably should). Retrieve and set them explicitly here:
    df = framegetter.get_frame(0)
    geom = df.get_pad_geometry()
    beam = df.get_beam()
    mask = df.get_mask_flat()
    profiler = analysis.saxs.ParallelRadialProfiler(
        framegetter=framegetter,
        pad_geometry = geom,
        beam = beam,
        mask = mask,
        **runstats_conf
    )
    profiler.process_frames()
    radials_dict = profiler.to_dict()
    if os.path.isfile(RUNNING_file):
        os.remove(RUNNING_file)
    return radials_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", type=int, default=None, help="Run number")
    parser.add_argument("--start", type=int, default=0, help="start frame number")
    parser.add_argument("--stop",type=int, default=None, help="stop frame number")
    parser.add_argument("-j", "--n_processes", type=int, default=12, help="Number of parallel processes")
    parser.add_argument("-d", "--detector", type=str, default='jungfrau', help="Detector to analyze (default=jungfrau, can also be epix.)")
    args = parser.parse_args()
    print(f"Fetching radials...")
    radials_dict = get_radials(
        run_number=args.run, n_processes=args.n_processes, 
        start=args.start, stop=args.stop,
        detector=args.detector
    )
    print(radials_dict.keys())

    pw = pg.plot(title="Radials")
    for i in range(10):
        pw.plot(radials_dict['q_bins'], radials_dict['mean'][i])
    #putting this input() line here keeps the plot open until you press enter on the terminal,
    #otherwise the pyqtgraph plot will immediately close as the script exits.
    #can also just put python -i script.py at the command line to enter interpreter state instead.
    input()

