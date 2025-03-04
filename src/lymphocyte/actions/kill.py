import logging
from dataclasses import dataclass

import psutil

from lymphocyte.actions.action import Action

log = logging.getLogger(__name__)


@dataclass
class KillAction(Action):
    """Action to kill a process given a uid.

    Args:
        Action (Action): Base Action class
    """

    uid: int

    async def perform(self) -> None:
        """Perform the killaction by killing the process. Logs if this successful or insuccesful."""
        procs = [p for p in psutil.process_iter() if p.uids().real == self.uid]
        for proc in procs:
            try:
                proc.kill()
                log.info("Killed %s", str(proc))
            except psutil.NoSuchProcess:
                log.debug("No such process %s", str(proc))
            except psutil.AccessDenied:
                log.exception("Access denied killing process %s", str(proc))
            except:
                log.exception("Error while killing")
                raise
