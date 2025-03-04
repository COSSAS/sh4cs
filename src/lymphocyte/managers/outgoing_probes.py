from lymphocyte.events.bus import EventBus


class OutgoingProbesManager:
    """Manager keeping the state of Of outgoing probes (health, readiness, and liveness).

    Returns:
        bool: status
    """

    _event_bus: EventBus

    _status: bool

    def __init__(self, event_bus: EventBus, name: str, initial_status: bool) -> None:
        """Constructs an OutgoingProbesManager.

        Args:
            event_bus (EventBus): An event bus
            name (str): Name of the OutgoingProbesManager
            initial_status (bool): Initial status
        """
        self._event_bus = event_bus
        self._name = name
        self._status = initial_status

    def status(self) -> bool:
        """Get current status.

        Returns:
            bool: Current status.
        """
        return self._status

    def set(self, status: bool) -> None:
        """Set current status.

        Args:
            status (bool): Current status to set.
        """
        self._status = status
