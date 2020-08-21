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
        atqueue = salobj.Remote(domain, 'ScriptQueue', index=2)
        start_tasks.append(atqueue.start_task)

    if not opts.no_mtq:
        mtqueue = salobj.Remote(domain, 'ScriptQueue', index=1)
        start_tasks.append(mtqueue.start_task)

    if not opts.no_w:
        watcher = salobj.Remote(domain, 'Watcher')
        start_tasks.append(watcher.start_task)

    await asyncio.gather(*start_tasks)

    enabled_state = salobj.State.ENABLED

    enable_tasks = []
    if not opts.no_atq:
        task = salobj.set_summary_state(atqueue, enabled_state)
        enable_tasks.append(task)

    if not opts.no_mtq:
        task = salobj.set_summary_state(mtqueue, enabled_state)
        enable_tasks.append(task)

    if not opts.no_w:
        task = salobj.set_summary_state(watcher, enabled_state, settingsToApply=opts.watcher_settings)
        enable_tasks.append(task)

    await asyncio.gather(*enable_tasks)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-atq", dest="no_atq", action="store_true")
    parser.add_argument("--no-mtq", dest="no_mtq", action="store_true")
    parser.add_argument("--no-w", dest="no_w", action="store_true")
    parser.add_argument("--watcher-settings", dest="watcher_settings", default="tucson")

    args = parser.parse_args()

    asyncio.run(main(args))
