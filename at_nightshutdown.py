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
        atcs = ATCS(domain, intended_usage=ATCSUsages().Shutdown)
        start_tasks.append(atcs.start_task)

    if not opts.no_la:
        latiss = LATISS(domain, intended_usage=LATISSUsages().StateTransition)
        start_tasks.append(latiss.start_task)

    await asyncio.gather(*start_tasks)

    shutdown_tasks = []
    if not opts.no_la:
        if opts.full:
            shutdown_tasks.append(latiss.set_state(salobj.state.OFFLINE))
        else:
            shutdown_tasks.append(latiss.standby())

    if not opts.no_at:
        shutdown_tasks.append(atcs.shutdown())
        # shutdown_tasks.append(at_shutdown(atcs))

    await asyncio.gather(*shutdown_tasks)

    if opts.full and not opts.no_at:
        await atcs.set_state(salobj.state.OFFLINE)

async def at_shutdown(atcs):
    await atcs.point_azel(target_name="Park position",
                          az=atcs.tel_park_az,
                          el=atcs.tel_park_el,
                          wait_dome=False)
    await atcs.close_m1_cover()
    await atcs.close_dome()
    await atcs.slew_dome_to(az=atcs.dome_park_az)
    await atcs.standby()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-la", dest="no_la", action="store_true")
    group.add_argument("--no-at", dest="no_at", action="store_true")
    group.add_argument("--full", dest="full", action="store_true")

    args = parser.parse_args()

    asyncio.run(main(args))
