from ingestion import Ingestor


def test_ingestor_placeholder() -> None:
    ingest = Ingestor()
    assert isinstance(ingest, Ingestor)
    assert Ingestor.__doc__ is not None
    assert "placeholder" in Ingestor.__doc__.lower()
