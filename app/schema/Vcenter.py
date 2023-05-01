
def schema_vcenter():
    """
    Vcenter Schema for API Validation
    :return:
    """
    schema = {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["url", "username", "password"],
            }
    return schema