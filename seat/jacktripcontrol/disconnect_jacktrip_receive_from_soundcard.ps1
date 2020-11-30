$cached_ip_path=[Environment]::GetEnvironmentVariable("JTC_REMOTE_IP_SETTING", "User")

function Get-WSL2IPAdrress {
  return (wsl hostname -I).Trim()
}

$client_ip=Get-WSL2IPAdrress
"client:"
$client_ip

# disconnect jacktrip from local soundcard
& 'C:/Program Files (x86)/Jack/jack_disconnect.exe' ($client_ip + ':receive_1') system:playback_1
& 'C:/Program Files (x86)/Jack/jack_disconnect.exe' ($client_ip + ':receive_2') system:playback_2
