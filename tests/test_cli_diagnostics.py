import subprocess, unittest
from unittest.mock import patch
from proton_sync_engine.cli_diagnostics import CliError,parse_version,detect_version,classify_error

class CliDiagnosticsTests(unittest.TestCase):
    def test_detect_installed_format(self):
        text='Proton Drive CLI cli-drive@0.9.0+75612299\nProton Drive SDK js@0.22.2+75612299\nYou are running the latest version.\n'
        self.assertEqual(parse_version(text).cli,'0.9.0')
        self.assertEqual(parse_version(text).sdk,'0.22.2')
        with patch('proton_sync_engine.cli_diagnostics.subprocess.run',return_value=subprocess.CompletedProcess([],0,text,'')) as run:
            self.assertEqual(detect_version('/fake/cli').cli,'0.9.0')
            run.assert_called_once_with(['/fake/cli','--version'],capture_output=True,text=True,timeout=8,check=False)
    def test_invalid_versions_fail_closed(self):
        for text in ('', '0.9.0','Proton Drive CLI cli-drive@unknown\n'):
            with self.assertRaises(ValueError):parse_version(text)
        with patch('proton_sync_engine.cli_diagnostics.subprocess.run',side_effect=subprocess.TimeoutExpired('cli',8)):
            with self.assertRaisesRegex(RuntimeError,'cli_version_timeout'):detect_version('/fake/cli')
    def test_errors_do_not_echo_secrets(self):
        cases=[('401 token SECRET',CliError.AUTH),('429 token SECRET',CliError.RATE_LIMIT),('Datei oder Ordner mit diesem Namen existiert bereits.',CliError.CONFLICT),('unexpected token SECRET',CliError.PROVIDER_ERROR)]
        for raw,expect in cases:
            self.assertEqual(classify_error(returncode=1,stderr=raw),expect)
        self.assertEqual(classify_error(returncode=1,timed_out=True),CliError.TIMEOUT)
        self.assertIsNone(classify_error(returncode=0,stderr='429'))
