import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


transcribe = load_module("podcast_transcribe", ROOT / "podcast-learning/scripts/transcribe.py")
fill_stats = load_module("podcast_fill_stats", ROOT / "podcast-learning/scripts/fill_report_stats.py")


class TranscribeTests(unittest.TestCase):
    def fake_whisper(self, directory, payload):
        executable = Path(directory) / "whisper-cli"
        executable.write_text(
            f"#!{sys.executable}\n"
            "import json, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            f"payload = {payload!r}\n"
            "prefix = Path(args[args.index('-of') + 1])\n"
            "prefix.with_suffix('.json').write_text(json.dumps(payload), encoding='utf-8')\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)

    def test_default_model_path_is_user_relative(self):
        self.assertEqual(
            transcribe.DEFAULT_WHISPER_CPP_MODELS,
            str(Path.home() / "workspace" / "whisper.cpp" / "models"),
        )
        self.assertNotIn("/Users/jabe", transcribe.DEFAULT_WHISPER_CPP_MODELS)

    def test_download_only_requires_persistent_output_before_download(self):
        with mock.patch.object(transcribe, "download_audio") as download:
            with self.assertRaises(SystemExit) as caught:
                transcribe.main(["https://example.org/episode", "--download-only"])
        self.assertIn("--audio-out", str(caught.exception))
        download.assert_not_called()

    def test_cli_uses_fake_whisper_and_atomically_replaces_output(self):
        payload = {
            "transcription": [
                {"timestamps": {"from": "00:00:00,000", "to": "00:00:01,000"}, "text": " 你好 "},
                {"timestamps": {"from": "00:00:01,000", "to": "00:00:02,000"}, "text": "世界"},
            ],
            "result": {"language": "zh"},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fake_whisper(root, payload)
            audio = root / "audio.mp3"
            audio.write_bytes(b"audio")
            model_dir = root / "models"
            model_dir.mkdir()
            (model_dir / transcribe.MODEL_FILES["large-v3"]).write_bytes(b"model")
            (model_dir / transcribe.DEFAULT_VAD_FILE).write_bytes(b"vad")
            output = root / "episode.transcript.txt"
            output.write_text("complete old transcript\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"PATH": str(root)}):
                result = transcribe.main([
                    str(audio), "--out", str(output), "--model-dir", str(model_dir)
                ])
            self.assertEqual(result, 0)
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                "[00:00:00 -> 00:00:01] 你好\n[00:00:01 -> 00:00:02] 世界\n",
            )
            self.assertFalse(any(path.name.startswith(".episode.transcript.txt.") for path in root.iterdir()))

    def test_conversion_failure_preserves_existing_transcript(self):
        payload = {
            "transcription": [
                {"timestamps": {"from": "00:00:00,000", "to": "00:00:01,000"}, "text": "new"},
                {"text": "malformed"},
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fake_whisper(root, payload)
            audio = root / "audio.mp3"
            audio.write_bytes(b"audio")
            model_dir = root / "models"
            model_dir.mkdir()
            (model_dir / transcribe.MODEL_FILES["large-v3"]).write_bytes(b"model")
            (model_dir / transcribe.DEFAULT_VAD_FILE).write_bytes(b"vad")
            output = root / "episode.transcript.txt"
            output.write_text("complete old transcript\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"PATH": str(root)}):
                with self.assertRaises(KeyError):
                    transcribe.main([
                        str(audio), "--out", str(output), "--model-dir", str(model_dir)
                    ])
            self.assertEqual(output.read_text(encoding="utf-8"), "complete old transcript\n")


class ReportStatsTests(unittest.TestCase):
    def test_missing_and_unquoted_speech_rate_are_updated(self):
        for declaration in ("speech_rate_cjk: 1 字/min", "speech_rate_cjk: \"1 字/min\"", ""):
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "podcast-learning"
                transcripts = root / "reports/transcripts"
                transcripts.mkdir(parents=True)
                (transcripts / "raw.txt").write_text(
                    "[00:00:00 -> 00:00:10] 汉字汉字\n", encoding="utf-8"
                )
                report = root / "reports/episode.md"
                report.write_text(
                    "---\n"
                    "transcript_path: reports/transcripts/raw.txt\n"
                    "duration_seconds: 60\n"
                    f"{declaration}\n"
                    "---\n# Report\n",
                    encoding="utf-8",
                )
                with mock.patch.object(fill_stats, "ROOT", root):
                    fill_stats.check(report, dry=False)
                self.assertIn('speech_rate_cjk: "4 字/min"', report.read_text(encoding="utf-8"))

    def test_missing_sources_are_not_reported_as_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "episode.md"
            report.write_text("---\ntranscript_path: missing.txt\n---\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                differences = fill_stats.check(report, dry=True)
            self.assertEqual(differences, [])
            self.assertIn("未读取 raw", output.getvalue())
            self.assertNotIn("✓ 一致", output.getvalue())


if __name__ == "__main__":
    unittest.main()
