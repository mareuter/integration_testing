import argparse
import asyncio
import logging
import sys

from lsst.ts import salobj
from lsst.ts.observatory.control.auxtel.atcs import ATCS, ATCSUsages
from lsst.ts.observatory.control.auxtel.latiss import LATISS, LATISSUsages

async def main(opts):

    stream_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.level = logging.DEBUG

    domain = salobj.Domain()

    start_tasks = []
    if not opts.no_at:
        atcs = ATCS(domain, intended_usage=ATCSUsages().StartUp)
        start_tasks.append(atcs.start_task)

    if not opts.no_la:
        latiss = LATISS(domain, intended_usage=LATISSUsages().StateTransition)
        start_tasks.append(latiss.start_task)

    await asyncio.gather(*start_tasks)

    enable_tasks = []
    if not opts.no_la:
        le = latiss.enable(settings={"atcamera": "Normal",
                                     "atarchiver": "normal",
                                     "atheaderservice": None})
        enable_tasks.append(le)

    if not opts.no_at:
        ae = atcs.enable(settings={"athexapod": "ncsa_202002.yaml",
                                   "atdome": "test",
                                   "ataos": "default"})
        enable_tasks.append(ae)

    await asyncio.gather(*enable_tasks)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-la", dest="no_la", action="store_true")
    group.add_argument("--no-at", dest="no_at", action="store_true")

    args = parser.parse_args()

    asyncio.run(main(args))
