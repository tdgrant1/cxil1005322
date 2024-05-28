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

@memory.cache(ignore=["n_processes"])
def get_runstats(run_number=1, n_processes=1, max_frames=1e7, max_sum=None, min_sum=None, start=0, stop=None, step=1, histogram=True, pixel_threshold=None):
    r"""Fetches some PAD statistics for a run.  See reborn docs."""
    conf = config.get_config(run_number)
    if pixel_threshold is not None:
        print(pixel_threshold)
        pp_suffix = f"_pt_{pixel_threshold}"
        conf['runstats']['checkpoint_file'] =conf['runstats']['checkpoint_file'] +  pp_suffix
        conf['runstats']['log_file'] = conf['runstats']['log_file'] + pp_suffix
        print(conf["runstats"]["log_file"])
    log_file = os.path.dirname(conf["runstats"]["log_file"])
    if not os.path.isdir(log_file):
        if not os.path.isdir(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        os.mkdir(log_file)
    RUNNING_file = log_file + "/RUNNING"
#    if os.path.isfile(RUNNING_file):
#        raise ValueError(f"somebody else is running {run_number}!\n remove file {RUNNING_file} if the job has for sure terminated")
    with open(RUNNING_file, 'w') as f:
        f.close()
    runstats_conf = conf["runstats"]
    if stop is None:
        runstats_conf["stop"] = int(max_frames)
    else:
        runstats_conf["stop"] = stop
    runstats_conf["start"] = start
    runstats_conf["step"] = step
    runstats_conf["n_processes"] = n_processes
    if histogram == False:
        runstats_conf["histogram_params"] = None
    detectors = conf["pad_detectors"]
    for d in detectors:
        d["mask"] = None
    pp = None
    if pixel_threshold is not None:
        def _thresh(self, dat):
            x = dat.get_raw_data_flat()
            x[x < pixel_threshold] = 0
            dat.set_raw_data(x)
            return dat
        pp = [_thresh]
    framegetter = LCLSFrameGetter(
        run_number=run_number,
        max_events=max_frames,
        experiment_id=conf["experiment_id"],
        pad_detectors=detectors,
        cachedir=conf["cachedir"],
        postprocessors=pp,
        photon_wavelength_pv=conf["photon_wavelength_pv"]
    )
    padstats = analysis.runstats.ParallelPADStats(
        framegetter=framegetter,  # max_sum=max_sum, min_sum=min_sum,
        **runstats_conf
    )
    padstats.process_frames()
    stats = padstats.to_dict()
    if os.path.isfile(RUNNING_file):
        os.remove(RUNNING_file)
    return stats


def combine_runstats(run_numbers, max_frames=1e7):
    r""" Combine runstats from several runs.  Note that it makes no sense to combine some things such
    as the beam and PAD geometry.  As of now, we only combine the pixel histograms for the purpose of
    calibrating the detector across multiple runs."""
    stats = get_runstats(run_number=run_numbers[0])
    stats["histogram"] = 0
    stats["sum"] = 0
    stats["sum2"] = 0
    stats["counts"] = 0
    stats["n_frames"] = 0
    stats["wavelengths"] = np.zeros(0)
    print('run_numbers', run_numbers)
    for r in run_numbers:
        s = get_runstats(run_number=r, max_frames=max_frames)
        for k in ["histogram", "sum", "sum2", "n_frames", "counts"]:
            stats[k] += s[k]
        for k in ["wavelengths", "percentiles"]:
            stats[k] = np.concatenate([stats[k], s[k]])
        stats["min"] = np.minimum(stats["min"], s["min"])
        stats["max"] = np.maximum(stats["max"], s["max"])
    return stats



def view_runstats(stats=None, geom=None, mask=None, hstgrm=True, **kwargs):
    """Convenience viewer for get_runstats. Accepts same arguments as get_runstats, along with a couple more:

    Arguments:
        geom (PADGeometryList): PAD geometry.
        mask (ndarray): PAD mask.
    """
    if stats is None:
        stats = get_runstats(**kwargs)
    if mask is not None:
        stats["mask"] = mask
    if geom is not None:
        stats["pad_geometry"] = geom

    # print(stats)
    geom = stats["pad_geometry"]
    beam = stats["beam"]
    c = config.default_config()
    n_q = c["profiles"]["n_bins"]
    q_range = np.array(c["profiles"]["q_range"])
    if hstgrm:
        hist = analysis.runstats.PixelHistogram(**stats["histogram_params"])
        hist.histogram = stats["histogram"].astype(float)
        php = stats["histogram_params"]
        adu_range = (php["bin_min"], php["bin_max"])
        if beam is not None:
            qb = hist.convert_to_q_histogram(
                pad_geometry=geom, n_q_bins=n_q, q_range=q_range, beam=beam, normalized=True
            )
            imv = imview(
                qb,
                ss_lims=q_range / 1e10,
                fs_lims=adu_range,
                ss_label="Q",
                fs_label="ADU",
                hold=False,
            )
            q_bins, median_profile = hist.get_median_profile(
                pad_geometry=geom, n_q_bins=n_q, q_range=q_range, beam=beam
            )
            imv.add_plot(q_bins / 1e10, median_profile)
    plot = pg.plot(stats["sums"], pen=None, symbol="o", symbolBrush="w")
    plot.setLabel("bottom", "Frame Number")
    plot.setLabel("left", "Integrated PAD Intensiy")
    analysis.runstats.view_padstats(stats, start=True, histogram=hstgrm)
    '''
    pv = analysis.runstats.view_padstats(stats, start=False, histogram=true)
    name = f"results/runstats/r{kwargs.get('run'):04d}/" 
    for i in range(pv.frame_getter.n_frames):
        name_ = f"{name}{pv.dataframe.get_frame_id()}.jpg"
        #print('saving screenshot ',name_,)
        pv.save_screenshot(name_)
        pv.show_next_frame()
    #pv.start()
    '''


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", type=int, default=154, help="Run number")
    parser.add_argument("--view", action="store_true", help="View stats")
    parser.add_argument("--start", type=int, default=0, help="start frame number")
    parser.add_argument("--stop",type=int, default=None, help="stop frame number")
    parser.add_argument("--step",type=int, default=1, help="number to skip between frames")
    parser.add_argument("--no_histogram", action="store_false", help="turn off histograms")
    parser.add_argument(
        "--max_sum",
        type=float,
        default=None,
        help="Maximum sum to include image in mean calculation",
    )
    parser.add_argument(
        "--min_sum",
        type=float,
        default=None,
        help="Minimum sum to include image in mean calculation",
    )
    parser.add_argument(
        "--max_events",
        type=int,
        default=1e7,
        help="Maximum number of events to process",
    )
    parser.add_argument(
        "-j", "--n_processes", type=int, default=12, help="Number of parallel processes"
    )
    parser.add_argument("-t", "--pixel_threshold", type=float, default=-999, help="Threshold runstats.")
    #parser.add_argument("--screenshots", action="store_true",help="save pyqt screenshots as jpg")
    args = parser.parse_args()
    print(f"Fetching runstats...")
    if args.pixel_threshold == -999:
        args.pixel_threshold = None
    stats = get_runstats(
        run_number=args.run, n_processes=args.n_processes, max_frames=args.max_events, 
        max_sum=args.max_sum, min_sum=args.min_sum, 
        start=args.start, stop=args.stop, step=args.step,
        histogram=args.no_histogram,
        pixel_threshold=args.pixel_threshold
    )
    if args.view:
        print("Viewing runstats...")
        view_runstats(stats, hstgrm=args.no_histogram, run=args.run)
#    else:
#        print("Saving screenshots...")
#        pv = analysis.runstats.view_padstats(stats, start=False, histogram=args.no_histogram)
#        name = f"results/runstats/r{args.run:04d}/" 
#        for i in range(pv.frame_getter.n_frames):
#            name_ = f"{name}{pv.dataframe.get_frame_id()}.jpg"
#            pv.save_screenshot(name_)
#            pv.show_next_frame()
