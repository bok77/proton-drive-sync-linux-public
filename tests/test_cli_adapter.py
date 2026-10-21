import subprocess,unittest
from unittest.mock import patch
from proton_sync_engine.cli_adapter import execute
from proton_sync_engine.cli_diagnostics import CliError

class CliAdapterTests(unittest.TestCase):
    def test_success_returns_readback_json(self):
        with patch('proton_sync_engine.cli_adapter.subprocess.run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')) as run:
            result=execute('/fake/cli','filesystem','info','/test','-j',timeout=4)
        self.assertEqual(result.stdout,'{"ok":true}')
        self.assertEqual(result.returncode,0)
        self.assertIsNone(result.error_class)
        run.assert_called_once_with(['/fake/cli','filesystem','info','/test','-j'],capture_output=True,text=True,timeout=4,check=False)
    def test_classified_failures_never_reveal_stderr_or_retry(self):
        for code,raw,expected in [(1,'401 TOKEN_PRIVATE',CliError.AUTH),(1,'429 TOKEN_PRIVATE',CliError.RATE_LIMIT),(1,'Datei oder Ordner mit diesem Namen existiert bereits. TOKEN_PRIVATE',CliError.CONFLICT),(2,'TOKEN_PRIVATE',CliError.PROVIDER_ERROR)]:
            with patch('proton_sync_engine.cli_adapter.subprocess.run',return_value=subprocess.CompletedProcess([],code,'',raw)) as run:
                result=execute('/fake/cli','filesystem','upload','-f','skip','/tmp/a','/test')
            self.assertEqual(result.error_class,expected)
            self.assertNotIn('TOKEN_PRIVATE',repr(result))
            self.assertEqual(run.call_count,1)
    def test_timeout_and_missing_executable_fail_closed(self):
        for exception,expected in [(subprocess.TimeoutExpired('cli',2),CliError.TIMEOUT),(FileNotFoundError('private path'),CliError.PROVIDER_ERROR)]:
            with patch('proton_sync_engine.cli_adapter.subprocess.run',side_effect=exception) as run:
                result=execute('/fake/cli','filesystem','upload','/tmp/a','/test')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.error_class,expected)
            self.assertEqual(run.call_count,1)
