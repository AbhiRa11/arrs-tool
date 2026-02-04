"""Custom exceptions for ARRS system."""


class ARRSException(Exception):
    """Base exception for ARRS system."""
    pass


class CrawlerException(ARRSException):
    """Crawler-related exceptions."""
    pass


class ParserException(ARRSException):
    """Parser-related exceptions."""
    pass


class EngineException(ARRSException):
    """Engine-related exceptions."""
    pass


class SimulationException(ARRSException):
    """Simulation-related exceptions."""
    pass


class StorageException(ARRSException):
    """Storage-related exceptions."""
    pass
