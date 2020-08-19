import argparse
import asyncio
import logging
import sys

from astropy.time import Time

from lsst.ts import salobj
from lsst.ts.observatory.control.maintel.mtcs import MTCS, MTCSUsages
from lsst.ts.observatory.control.maintel.comcam import ComCam, ComCamUsages

import helpers
import mt_utils

async def main(opts):

    stream_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.level = logging.DEBUG

    domain = salobj.Domain()

    start_tasks = []
    if not opts.no_mt:
        mtcs = MTCS(domain, intended_usage=MTCSUsages().Slew)
        start_tasks.append(mtcs.start_task)

    comcam = ComCam(domain, intended_usage=ComCamUsages().TakeImage)
    start_tasks.append(comcam.start_task)

    await asyncio.gather(*start_tasks)

    if not opts.no_mt:
        mtcs.check.dome = False
        mtcs.check.mtdometrajectory = False

    do_bias, do_dark, do_flat = helpers.calibs_to_do(opts.calibs)

    date = Time.now()
    group_id = f'CALSET_{date.tai.strftime("%Y%m%d_%H%M")}'

    if do_bias:
        await comcam.take_bias(nbias=opts.nbias, group_id=group_id)

    if do_dark:
        await comcam.take_darks(exptime=opts.dark_exptime, ndarks=opts.ndarks, group_id=group_id)

    if do_flat:
        if not opts.no_mt and not opts.no_slew:
            await mt_utils.slew_to_flatfield(mtcs)

        await comcam.take_flats(exptime=opts.flat_exptime, nflats=opts.nflats, group_id=group_id)

        if not opts.no_mt and not opts.no_slew:
            await mt_utils.slew_to_park(mtcs)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-mt", dest="no_mt", action="store_true")
    parser.add_argument("--no-slew", dest="no_slew", action="store_true")
    parser.add_argument("--nbias", dest="nbias", type=int, default=1)
    parser.add_argument("--ndarks", dest="ndarks", type=int, default=1)
    parser.add_argument("--nflats", dest="nflats", type=int, default=1)
    parser.add_argument("--dark-exptime", dest="dark_exptime", type=float, default=5.0)
    parser.add_argument("--flat-exptime", dest="flat_exptime", type=float, default=2.0)
    parser.add_argument("--calibs", dest="calibs", choices=helpers.CALIB_OPTIONS, default="bias")

    args = parser.parse_args()

    asyncio.run(main(args))
