function Get-WSL2IPAdrress {
  return (wsl hostname -I).Trim()
}

$client_ip=Get-WSL2IPAdrress
"client:"
$client_ip

# start the metronome process in new window
Start-Process -FilePath "wsl" `
  -ArgumentList "-u root jack_metro --bpm 100"

# wait a moment for the metronome to expose its ports
# show the list of ports (useful for debugging)
# connect up the metronome to jacktrip
wsl -u root bash -c "sleep 0.1; jack_lsp; jack_connect metro:100_bpm JackTrip:send_1"

# connect jactrip to local soundcard
& 'C:/Program Files (x86)/Jack/jack_connect.exe' ($client_ip + ':receive_1') system:playback_1

# user check
$dummy = Read-Host -Prompt 'Verify that you can hear the audio.../nPress return to end'

# disconnect and end the metronome process
& 'C:/Program Files (x86)/Jack/jack_disconnect.exe' ($client_ip + ':receive_1') system:playback_1
wsl -u root bash -c "jack_disconnect metro:100_bpm JackTrip:send_1; pkill -9 -f jack_metro"
