import importlib.util
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ai-practice/src"
TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None


class DatasetSafetyTests(unittest.TestCase):
    def test_remote_code_is_opt_in_and_loading_has_no_cache_scan(self):
        sys.path.insert(0, str(SRC))
        import load_local_dataset

        calls = []

        class Dataset(list):
            column_names = ["text"]

        def load_dataset(name, **kwargs):
            calls.append((name, kwargs))
            return Dataset([{"text": "example"}])

        fake = types.SimpleNamespace(
            load_dataset=load_dataset,
            load_from_disk=lambda *_args: (_ for _ in ()).throw(AssertionError("unexpected local read")),
        )
        with mock.patch.dict(sys.modules, {"datasets": fake}):
            result = load_local_dataset.load_and_show_dataset(
                dataset_name="openai/gsm8k", num_samples=1
            )
        self.assertEqual(len(result), 1)
        self.assertEqual(calls[0][1]["trust_remote_code"], False)


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is an optional AI Practice dependency")
class TransformerContractTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SRC))
        import torch
        from transformer_core import TransformerConfig

        self.torch = torch
        self.config = TransformerConfig(
            batch_size=2,
            context_length=4,
            d_model=8,
            num_blocks=1,
            num_heads=2,
            dropout=0.0,
            max_iters=1,
            eval_interval=1,
            eval_iters=1,
            device="cpu",
        )

    def test_import_does_not_download_train_or_write_in_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import model; import inference; assert model.TransformerLanguageModel is not None",
                ],
                cwd=directory,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_dense_forward_backward_and_checkpoint_roundtrip(self):
        from transformer_core import TransformerLanguageModel

        torch = self.torch
        torch.manual_seed(7)
        model = TransformerLanguageModel(12, self.config)
        tokens = torch.randint(0, 12, (2, 4))
        targets = torch.randint(0, 12, (2, 4))
        logits, loss = model(tokens, targets)
        self.assertEqual(tuple(logits.shape), (2, 4, 12))
        loss.backward()
        self.assertTrue(any(p.grad is not None for p in model.parameters()))
        self.assertIn("transformer_blocks.1.weight", model.state_dict())
        self.assertIn("transformer_blocks.0.feed_forward_layer.ffn.0.weight", model.state_dict())

        model.eval()
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "model.pt"
            torch.save(model.state_dict(), checkpoint)
            restored = TransformerLanguageModel(12, self.config)
            restored.load_state_dict(torch.load(checkpoint, weights_only=True))
            restored.eval()
        with torch.no_grad():
            self.assertTrue(torch.equal(model(tokens)[0], restored(tokens)[0]))

    def test_moe_forward_backward_preserves_component_state_names(self):
        from moe_model import MoEConfig, MoETransformerLanguageModel

        torch = self.torch
        config = MoEConfig(
            batch_size=2,
            context_length=4,
            d_model=8,
            num_blocks=1,
            num_heads=2,
            dropout=0.0,
            device="cpu",
        )
        torch.manual_seed(7)
        model = MoETransformerLanguageModel(12, config)
        tokens = torch.randint(0, 12, (2, 4))
        targets = torch.randint(0, 12, (2, 4))
        logits, loss = model(tokens, targets)
        self.assertEqual(tuple(logits.shape), (2, 4, 12))
        loss.backward()
        self.assertTrue(any(p.grad is not None for p in model.parameters()))
        keys = model.state_dict()
        self.assertIn("transformer_blocks.0.moe_layer.router.gate.weight", keys)
        self.assertIn("transformer_blocks.0.moe_layer.experts.0.ffn.0.weight", keys)
        self.assertIn("transformer_blocks.0.multi_head_attention_layer.heads.0.key_layer.weight", keys)


if __name__ == "__main__":
    unittest.main()
