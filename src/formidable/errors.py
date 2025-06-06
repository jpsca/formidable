"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

INVALID = "invalid"
REQUIRED = "required"

GT = "gt"
GTE = "gte"
LT = "lt"
LTE = "lte"
MULTIPLE_OF = "multiple_of"

MIN_ITEMS = "min_items"
MAX_ITEMS = "max_items"

MIN_LENGTH = "min_length"
MAX_LENGTH = "max_length"
PATTERN = "pattern"

PAST_DATE = "past_date"
FUTURE_DATE = "future_date"
AFTER_DATE = "after_date"
BEFORE_DATE = "before_date"

AFTER_TIME = "after_time"
BEFORE_TIME = "before_time"
PAST_TIME = "past_time"
FUTURE_TIME = "future_time"

MESSAGES = {
    INVALID: "Invalid value for '{name}'",
    REQUIRED: "Field '{name}' is required",

    GT: "'{name}' must be greater than {gt}",
    GTE: "'{name}' must be greater or equal than {gte}",
    LT: "'{name}' must be less than {lt}",
    LTE: "'{name}' must be less or equal than {lte}",
    MULTIPLE_OF: "'{name}' must multiple of {multiple_of}",

    MIN_ITEMS: "'{name}' must have at least {min_length} items",
    MAX_ITEMS: "'{name}' must have at most {max_length} items",

    MIN_LENGTH: "'{name}' must have at least {min_length} characters",
    MAX_LENGTH: "'{name}' must have at most {max_length} characters",
    PATTERN: "'{name}' must match the pattern `{pattern}`",

    PAST_DATE: "'{name}' must be a date in the past",
    FUTURE_DATE: "'{name}' must be a date in the future",
    AFTER_DATE: "'{name}' must be after {after_date}",
    BEFORE_DATE: "'{name}' must be before {before_date}",

    AFTER_TIME: "'{name}' must be after {after_time}",
    BEFORE_TIME: "'{name}' must be before {before_time}",
    PAST_TIME: "'{name}' must be a time in the past",
    FUTURE_TIME: "'{name}' must be a time in the future",
}
