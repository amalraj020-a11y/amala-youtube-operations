param(
  [Parameter(Mandatory=$true)][string]$ScriptPath,
  [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
  $speech.SelectVoice('Microsoft Zira Desktop')
  $speech.Rate = 0
  $speech.SetOutputToWaveFile($OutputPath)
  $speech.Speak([System.IO.File]::ReadAllText($ScriptPath))
  $speech.SetOutputToNull()
} finally {
  $speech.Dispose()
}
