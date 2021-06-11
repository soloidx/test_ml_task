class BadConfigurationError(Exception):
    pass


class InitializationError(BadConfigurationError):
    pass


class ClassifierError(Exception):
    pass
