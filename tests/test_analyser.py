"""Offline tests for scripts/github_analyser.py. Run: python3 -m unittest discover tests"""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import github_analyser as ga  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def section(name, user, **kw):
    return ga.build_section(json.loads((FIX / name).read_text()), user, **kw)


def rows(text):
    return [l for l in text.splitlines() if l.startswith("| ") and not l.startswith("| ---") and "Repo" not in l]


def unescaped_pipes(line):
    return sum(1 for i, ch in enumerate(line) if ch == "|" and (i == 0 or line[i - 1] != "\\"))


class RealData(unittest.TestCase):
    def setUp(self):
        self.out = section("kremendev.json", "kremendev")

    def test_last_five_repos_newest_first_profile_repo_excluded(self):
        names = [r.split("[**")[1].split("**]")[0].replace("\\_", "_") for r in rows(self.out)]
        self.assertEqual(names, ["github-profile-builder", "world-of-agents", "good-prompt-reminder",
                                 "CollegeTasks_Modal", "pinhole-manual"])
        self.assertNotIn("](https://github.com/kremendev/kremendev)", self.out)

    def test_latest_change_and_counts(self):
        woa = next(r for r in rows(self.out) if "world-of-agents" in r)
        self.assertIn("v2: why run 2 started in auto", woa)
        self.assertIn("+12 more in 30 days", woa)
        self.assertIn("Last 30 days: 22 commits across 5 repos, mostly TypeScript", self.out)

    def test_status_by_age(self):
        st = {r.split("[**")[1].split("**]")[0]: r[2] for r in rows(self.out)}
        self.assertEqual(st["world-of-agents"], "🟢")      # 6 days old
        self.assertEqual(st["good-prompt-reminder"], "🟡")  # 10 days old

    def test_table_cells_stay_intact(self):
        for r in rows(self.out):
            self.assertEqual(unescaped_pipes(r), 5, r)


class Attacks(unittest.TestCase):
    def setUp(self):
        self.out = section("attacks.json", "victim")

    def test_no_html_or_outbound_links(self):
        low = self.out.lower()
        for bad in ("<img", "<script", "evil.example", "javascript:", "‮"):
            self.assertNotIn(bad, low)

    def test_only_owner_meaningful_commits(self):
        for bad in ("PWNED", "dependabot", "WIP", "unlinked", "Merge pull request", "ancient"):
            self.assertNotIn(bad, self.out)

    def test_excluded_repos(self):
        for bad in ("forked-thing", "old-archive", "secret-plans", "](https://github.com/victim/victim)"):
            self.assertNotIn(bad, self.out)

    def test_escaping_and_truncation(self):
        target = next(r for r in rows(self.out) if "target" in r)
        self.assertEqual(unescaped_pipes(target), 5, target)
        self.assertIn("Fix \\| bug \\[click me\\]", target)  # link syntax made inert
        self.assertIn("…", target)                           # long message cut
        self.assertIn("@⁠someone", target)              # no @mention link

    def test_releases(self):
        self.assertIn("**Recently shipped:**", self.out)
        self.assertIn("v2.0.0 \\| big one", self.out)
        self.assertNotIn("Draft", self.out)

    def test_quiet_repo_shows_no_commits(self):
        quiet = next(r for r in rows(self.out) if "quiet" in r)
        self.assertTrue(quiet.startswith("| ⚪"))
        self.assertIn("no commits in the last 30 days", quiet)


class ReadmeUpdate(unittest.TestCase):
    def test_idempotent_and_keeps_the_rest(self):
        sec = section("kremendev.json", "kremendev")
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "README.md"
            p.write_text(f"# Hi\n\nbefore\n\n{ga.START}\nold\n{ga.END}\n\nafter\n")
            self.assertTrue(ga.update_readme(p, sec))
            self.assertFalse(ga.update_readme(p, sec))  # same data, no change, no commit
            text = p.read_text()
            self.assertTrue(text.startswith("# Hi\n\nbefore\n\n"))
            self.assertTrue(text.endswith("\n\nafter\n"))
            self.assertNotIn("\nold\n", text)

    def test_missing_markers_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "README.md"
            p.write_text("# no markers here\n")
            with self.assertRaises(SystemExit):
                ga.update_readme(p, "x")

    def test_exclude_list(self):
        out = section("kremendev.json", "kremendev", exclude={"CollegeTasks_Modal"})
        self.assertNotIn("CollegeTasks", out)
        self.assertIn("pinhole-ai", out)  # the next most recent repo moves up


class RankingIgnoresPushNoise(unittest.TestCase):
    """Regression: a history rewrite force-pushed three repos, which reset their
    pushed_at, and the old ranking put a repo nobody had worked on into the table."""

    def test_force_push_does_not_count_as_activity(self):
        data = json.loads((FIX / "kremendev.json").read_text())
        rewrite_time = "2026-11-03T11:50:00Z"
        for r in data["repos"]:
            if r["name"] in ("pinhole-ai", "pinhole-manual", "good-prompt-reminder"):
                r["pushed_at"] = rewrite_time
        data["detail"]["pinhole-ai"] = {"releases": [], "commits": [{
            "html_url": "https://github.com/kremendev/pinhole-ai/commit/d86388a",
            "author": {"login": "kremendev", "type": "User"}, "parents": [{"sha": "x"}],
            "commit": {"message": "Package and upload PDF + zipped site", "author": {"date": "2026-10-05T21:02:42Z"}}}]}
        out = ga.build_section(data, "kremendev")
        names = [r.split("[**")[1].split("**]")[0].replace("\\_", "_") for r in rows(out)]
        self.assertEqual(names, ["github-profile-builder", "world-of-agents", "good-prompt-reminder",
                                 "CollegeTasks_Modal", "pinhole-manual"])


class ImagesAreOffLimits(unittest.TestCase):
    """Once the banner and other images exist, the analyser must never change them."""

    PROFILE = ('<p align="center"><img src="./assets/banner.svg" alt="banner" width="100%"></p>\n\n'
               "## About\n\n![stack](https://skillicons.dev/icons?i=ts)\n\n"
               f"{ga.START}\nold\n{ga.END}\n\n"
               '<img src="https://github.com/u/u/raw/output/game.gif">\n')

    def test_everything_outside_the_markers_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "README.md"
            p.write_text(self.PROFILE)
            ga.update_readme(p, section("kremendev.json", "kremendev"))
            self.assertEqual(ga.outside(p.read_text()), ga.outside(self.PROFILE))
            for img in ("./assets/banner.svg", "skillicons.dev", "game.gif"):
                self.assertEqual(p.read_text().count(img), 1)

    def test_section_never_contains_images(self):
        for out in (section("kremendev.json", "kremendev"), section("attacks.json", "victim")):
            self.assertIsNone(ga.IMAGE.search(out))

    def test_image_guard_fires(self):
        data = json.loads((FIX / "kremendev.json").read_text())
        data["repos"][2]["language"] = "<img src=x>TypeScript"  # tags are stripped first...
        self.assertIsNone(ga.IMAGE.search(ga.build_section(data, "kremendev")))
        with self.assertRaises(SystemExit):                      # ...and anything left is refused
            ga.build_section(data, "kremendev", title="![x](y)")

    def test_only_readme_can_be_written(self):
        with tempfile.TemporaryDirectory() as d:
            svg = pathlib.Path(d) / "banner.svg"
            svg.write_text(f"{ga.START}{ga.END}")
            with self.assertRaises(SystemExit):
                ga.update_readme(svg, "x")
            self.assertEqual(svg.read_text(), f"{ga.START}{ga.END}")


if __name__ == "__main__":
    unittest.main()
