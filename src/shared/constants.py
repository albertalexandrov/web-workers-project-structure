import os
from enum import StrEnum, auto


class EnvironmentEnum(StrEnum):
    LOCAL = "LOCAL"
    STAGE = "STAGE"
    PROD = "PROD"

    @classmethod
    def get_environment(cls):
        return cls(os.environ.get("ENVIRONMENT", "LOCAL"))
