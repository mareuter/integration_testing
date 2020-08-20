import argparse
import asyncio
import logging
import sys

from lsst.ts import salobj
from lsst.ts.observatory.control.maintel.mtcs import MTCS, MTCSUsages
from lsst.ts.observatory.control.maintel.comcam import ComCam, ComCamUsages

import mt_utils

async def main(opts):

    stream_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.level = logging.DEBUG

    domain = salobj.Domain()

    start_tasks = []

    if not opts.no_mt:
        mtcs = MTCS(domain, intended_usage=MTCSUsages().StartUp)
        start_tasks.append(mtcs.start_task)

    if not opts.no_cc:
        comcam = ComCam(domain, intended_usage=ComCamUsages().StateTransition)
        start_tasks.append(comcam.start_task)

    await asyncio.gather(*start_tasks)

    if not opts.no_mt:
        mtcs.check.dome = False
        mtcs.check.mtdometrajectory = False

    shutdown_tasks = []

    if not opts.no_cc:
        if opts.full:
            task = comcam.set_state(salobj.State.OFFLINE)
        else:
            task = comcam.standby()
        shutdown_tasks.append(task)

    if not opts.no_mt:
        if not opts.no_mt:
            await mt_utils.slew_to_park(mtcs)

        if opts.full:
            task = mtcs.set_state(salobj.State.OFFLINE)
        else:
            task = mtcs.standby()
        shutdown_tasks.append(task)

    await asyncio.gather(*shutdown_tasks)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-cc", dest="no_cc", action="store_true")
    group.add_argument("--no-mt", dest="no_mt", action="store_true")
    group.add_argument("--full", dest="full", action="store_true")

    args = parser.parse_args()

    asyncio.run(main(args))
