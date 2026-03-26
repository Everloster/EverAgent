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


def load_report_generator():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "github-trending-analyzer"
        / "report_generator.py"
    )
    spec = spec_from_file_location("report_generator", module_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_growth_label_matches_period():
    module = load_report_generator()
    assert module.get_growth_label("daily") == "今日增长"
    assert module.get_growth_label("weekly") == "本周增长"
    assert module.get_growth_label("monthly") == "本月增长"


def test_generate_summary_report_uses_period_growth_label(tmp_path):
    module = load_report_generator()
    output = tmp_path / "summary.md"
    repos = [
        {
            "owner": "acme",
            "repo": "rocket",
            "language": "Python",
            "stars": 1234,
            "today_stars": 56,
            "description": "Fast launch toolkit",
            "url": "https://github.com/acme/rocket",
        }
    ]

    module.generate_summary_report("weekly", repos, output)

    content = output.read_text(encoding="utf-8")
    assert "本周增长" in content
    assert "今日增长" not in content


def test_generate_project_report_uses_period_growth_label(tmp_path):
    module = load_report_generator()
    output = tmp_path / "project.md"
    repo_data = {
        "owner": "acme",
        "repo": "rocket",
        "description": "Fast launch toolkit",
        "stars": 1234,
        "forks": 56,
        "language": "Python",
        "today_stars": 78,
        "url": "https://github.com/acme/rocket",
    }
    analysis_data = {
        "summary": "A strong repo",
        "languages": {"Python": 100},
        "contributors": [],
        "releases": [],
    }

    module.generate_project_report(repo_data, analysis_data, output, period="monthly")

    content = output.read_text(encoding="utf-8")
    assert "本月增长" in content
    assert "今日增长" not in content
