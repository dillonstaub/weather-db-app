import data_ingestion

def resolve_ingestData(obj, info):
    try:
        data_ingestion.ingestion_handler()
        payload = {
            "ingestion_status": "ingestion complete"
            }
    except Exception:
        payload = {
            "ingestion_status": "ingestion error"
            }
    return payload

def resolve_clearTable(obj, info):
    try:
        data_ingestion.clear_table()
        payload = {
            "truncation_status": "table truncate complete"
            }
    except Exception:
        payload = {
            "truncation_status": "table truncate error"
            }
    return payload