param(
  [Parameter(Mandatory=$true)][string]$ScriptPath,
  [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
  $preferred = $speech.GetInstalledVoices() | Where-Object { $_.Enabled } | Select-Object -First 1
  if ($null -eq $preferred) { throw 'No enabled Windows speech voice is installed' }
  $speech.SelectVoice($preferred.VoiceInfo.Name)
  $speech.Rate = 0
  $speech.SetOutputToWaveFile($OutputPath)
  $speech.Speak([System.IO.File]::ReadAllText($ScriptPath))
  $speech.SetOutputToNull()
} finally {
  $speech.Dispose()
}
