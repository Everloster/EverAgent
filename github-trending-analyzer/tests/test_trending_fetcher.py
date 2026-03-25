from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "github-trending-analyzer"
        / "trending_fetcher.py"
    )
    spec = spec_from_file_location("trending_fetcher", module_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_extract_today_stars_for_weekly():
    module = load_module()
    assert module._extract_today_stars("1,234 stars this week") == 1234


def test_parse_trending_repos_from_html():
    module = load_module()
    html = """
    <article class="Box-row">
      <h2><a href="/acme/rocket"> acme / rocket </a></h2>
      <p class="col-9 color-fg-muted my-1 pr-4">Fast launch toolkit</p>
      <span itemprop="programmingLanguage">Python</span>
      <a href="/acme/rocket/stargazers">1,234</a>
      <a href="/acme/rocket/forks">56</a>
      <span>78 stars today</span>
    </article>
    """
    repos = module.parse_trending_repos(html)
    assert len(repos) == 1
    assert repos[0]["owner"] == "acme"
    assert repos[0]["repo"] == "rocket"
    assert repos[0]["stars"] == 1234
    assert repos[0]["forks"] == 56
    assert repos[0]["today_stars"] == 78
