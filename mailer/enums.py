PRIORITY_MAPPING = {
    'high': '1',
    'medium': '2',
    'low': '3',
    'deferred': '4',
}

PRIORITIES = (
    (PRIORITY_MAPPING['high'], 'high'),
    (PRIORITY_MAPPING['medium'], 'medium'),
    (PRIORITY_MAPPING['low'], 'low'),
    (PRIORITY_MAPPING['deferred'], 'deferred'),
)

RESULT_MAPPING = {
    'success': '1',
    'don\'t send': '2',
    'failure': '3',
}

RESULT_CODES = (
    (RESULT_MAPPING['success'], 'success'),
    (RESULT_MAPPING['don\'t send'], 'don\'t send'),
    (RESULT_MAPPING['failure'], 'failure'),
)
