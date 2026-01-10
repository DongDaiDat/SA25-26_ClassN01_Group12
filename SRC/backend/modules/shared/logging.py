class RequestIDLogFilter:
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True
