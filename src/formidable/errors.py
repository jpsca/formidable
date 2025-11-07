"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

INVALID = "invalid"
REQUIRED = "required"
ONE_OF = "one_of"

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

INVALID_URL = "invalid_url"
INVALID_EMAIL = "invalid_email"
INVALID_SLUG = "invalid_slug"

MESSAGES = {
    INVALID: "Invalid value",
    REQUIRED: "Field is required",
    ONE_OF: "Must be one of {one_of}",

    GT: "Must be greater than {gt}",
    GTE: "Must be greater or equal than {gte}",
    LT: "Must be less than {lt}",
    LTE: "Must be less or equal than {lte}",
    MULTIPLE_OF: "Must multiple of {multiple_of}",

    MIN_ITEMS: "Must have at least {min_length} items",
    MAX_ITEMS: "Must have at most {max_length} items",

    MIN_LENGTH: "Must have at least {min_length} characters",
    MAX_LENGTH: "Must have at most {max_length} characters",
    PATTERN: "Invalid format",

    PAST_DATE: "Must be a date in the past",
    FUTURE_DATE: "Must be a date in the future",
    AFTER_DATE: "Must be after {after_date}",
    BEFORE_DATE: "Must be before {before_date}",

    AFTER_TIME: "Must be after {after_time}",
    BEFORE_TIME: "Must be before {before_time}",
    PAST_TIME: "Must be a time in the past",
    FUTURE_TIME: "Must be a time in the future",

    INVALID_URL: "Doesn't seem to be a valid URL",
    INVALID_EMAIL: "Doesn't seem to be a valid email address",
    INVALID_SLUG: "A valid “slug” can only have a-z letters, numbers, underscores, or hyphens"
}
