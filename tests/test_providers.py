import json
import tempfile
import unittest
from pathlib import Path

from evolean_lab.providers import Budget, CodexWorkspaceProvider, OpenAIAPIProvider, ProposalRequest


class ProviderTests(unittest.TestCase):
    def test_codex_provider_queues_structured_job(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request = ProposalRequest("strategist", "find proof plans", {}, {"proposals": "array"})
            response = CodexWorkspaceProvider(Path(directory)).propose(request)
            job = Path(response.usage["job_file"])
            self.assertTrue(job.is_file())
            self.assertEqual(json.loads(job.read_text(encoding="utf-8"))["id"], request.id)

    def test_api_provider_is_disabled_by_default(self) -> None:
        request = ProposalRequest("strategist", "find proof plans", {}, {}, Budget())
        with self.assertRaises(RuntimeError):
            OpenAIAPIProvider("configured-later").propose(request)


if __name__ == "__main__":
    unittest.main()
