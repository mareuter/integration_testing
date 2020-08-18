import argparse
import asyncio
import logging
import sys

from astropy.time import Time

from lsst.ts import salobj
from lsst.ts.observatory.control.maintel.mtcs import MTCS, MTCSUsages
from lsst.ts.observatory.control.maintel.comcam import ComCam, ComCamUsages

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

    date = Time.now()
    group_id = f'CALSET_{date.tai.strftime("%Y%m%d_%H%M")}'

    await comcam.take_bias(nbias=2, group_id=group_id)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-mt", dest="no_mt", action="store_true")

    args = parser.parse_args()

    asyncio.run(main(args))
