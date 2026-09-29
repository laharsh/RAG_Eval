from src.retriever import expand_with_neighbors, reciprocal_rank_fusion


def test_rrf_prefers_docs_in_both_lists():
    """Doc appearing in both lists should rank above single-list docs."""
    vector = ["a", "b", "c"]
    bm25 = ["b", "d", "e"]
    fused = reciprocal_rank_fusion([vector, bm25], k=60)
    assert fused[0] == "b"  # in both lists


def test_rrf_preserves_unique_docs():
    fused = reciprocal_rank_fusion([["x", "y"], ["y", "z"]])
    assert set(fused) == {"x", "y", "z"}


def test_expand_with_neighbors_uses_seq(monkeypatch):
    """Neighbor expansion pulls adjacent chunks by document order."""
    fake_registry = {
        "a": {"chunk_id": "a", "seq": 10, "content": "A", "source": "x", "page": 1},
        "b": {"chunk_id": "b", "seq": 11, "content": "B", "source": "x", "page": 1},
        "c": {"chunk_id": "c", "seq": 12, "content": "C", "source": "x", "page": 1},
    }
    import src.retriever as ret

    monkeypatch.setattr(ret, "_registry", fake_registry)
    monkeypatch.setattr(ret, "_by_seq", {10: "a", 11: "b", 12: "c"})

    expanded = expand_with_neighbors(["b"], window=1)
    assert expanded == ["a", "b", "c"]
