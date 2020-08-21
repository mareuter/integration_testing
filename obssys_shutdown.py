import argparse
import asyncio
import logging
import sys

from lsst.ts import salobj

async def main(opts):

    stream_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.level = logging.DEBUG

    domain = salobj.Domain()

    start_tasks = []

    domain = salobj.Domain()
    if not opts.no_atq:
        # AT ScriptQueue is index=2
        atqueue = salobj.Remote(domain, 'ScriptQueue', index=2)
        start_tasks.append(atqueue.start_task)

    if not opts.no_mtq:
        mtqueue = salobj.Remote(domain, 'ScriptQueue', index=1)
        start_tasks.append(mtqueue.start_task)

    if not opts.no_w:
        watcher = salobj.Remote(domain, 'Watcher')
        start_tasks.append(watcher.start_task)

    await asyncio.gather(*start_tasks)

    if opts.full:
        shutdown_state = salobj.State.OFFLINE
    else:
        shutdown_state = salobj.State.STANDBY

    shutdown_tasks = []
    if not opts.no_atq:
        task = salobj.set_summary_state(atqueue, shutdown_state)
        shutdown_tasks.append(task)

    if not opts.no_mtq:
        task = salobj.set_summary_state(mtqueue, shutdown_state)
        shutdown_tasks.append(task)

    if not opts.no_w:
        task = salobj.set_summary_state(watcher, shutdown_state)
        shutdown_tasks.append(task)

    await asyncio.gather(*shutdown_tasks)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-atq", dest="no_atq", action="store_true")
    group.add_argument("--no-mtq", dest="no_mtq", action="store_true")
    group.add_argument("--no-w", dest="no_w", action="store_true")
    group.add_argument("--full", dest="full", action="store_true")

    args = parser.parse_args()

    asyncio.run(main(args))
