"""Conservative contract smoke test; this is not a completion attestation."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class GameCompletionContractTests(unittest.TestCase):
    def test_schema_documents_server_only_no_client_mint(self):
        schema = json.loads((ROOT / 'contracts/tavix-game-completion-v1.schema.json').read_text())
        self.assertEqual(schema['properties']['schema']['const'], 'tavix.game-completion/v1')
        self.assertIn('finalStateDigest', schema['required'])
        self.assertIn('recipientId', schema['required'])
        self.assertFalse(schema['additionalProperties'])
        doc = (ROOT / 'docs/TAVIX_GAME_COMPLETION_REWARD_001.adoc').read_text()
        self.assertIn('not a sandboxed app', doc)
        self.assertIn('tavi.wallet-reward/v1', doc)
        self.assertIn('pending', doc)
        self.assertIn('offline', doc.lower())


if __name__ == '__main__':
    unittest.main()
