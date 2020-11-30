$cached_ip_path=[Environment]::GetEnvironmentVariable("JTC_REMOTE_IP_SETTING", "User")

function Get-WSL2IPAdrress {
  return (wsl hostname -I).Trim()
}

"Getting IP address of remote machine"
$client_ip = Get-Content -Path $cached_ip_path
"client:__" + $client_ip + "__"

# connect jactrip to local soundcard
& 'C:/Program Files (x86)/Jack/jack_connect.exe' ($client_ip + ':receive_1') system:playback_1
& 'C:/Program Files (x86)/Jack/jack_connect.exe' ($client_ip + ':receive_2') system:playback_2
