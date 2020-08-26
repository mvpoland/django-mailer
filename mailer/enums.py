PRIORITY_HIGH = "1"
PRIORITY_MEDIUM = "2"
PRIORITY_LOW = "3"
PRIORITY_DEFERRED = "4"

PRIORITIES = [
    (PRIORITY_HIGH, "high"),
    (PRIORITY_MEDIUM, "medium"),
    (PRIORITY_LOW, "low"),
    (PRIORITY_DEFERRED, "deferred"),
]

PRIORITY_MAPPING = dict((label, v) for v, label in PRIORITIES)


RESULT_MAPPING = {
    "success": "1",
    "don't send": "2",
    "failure": "3",
}

RESULT_CODES = (
    (RESULT_MAPPING["success"], "success"),
    (RESULT_MAPPING["don't send"], "don't send"),
    (RESULT_MAPPING["failure"], "failure"),
)
