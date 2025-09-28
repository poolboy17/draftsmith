import hydrate
import scaffold


def test_scaffold_and_hydrate_dry_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "1")
    # fresh cache for lru
    scaffold._scaffold_article_cached.cache_clear()
    hydrate.hydrate_article.cache_clear()
    out1 = scaffold.scaffold_article("topic", links=["http://a"])
    # DRY_RUN returns the last user message content; in scaffold that's the Links payload
    assert "http://a" in out1
    out2 = hydrate.hydrate_article("outline")
    assert "outline" in out2
