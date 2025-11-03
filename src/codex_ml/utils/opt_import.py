def try_import(name: str):
    try:
        return __import__(name)
    except Exception:
        return None
