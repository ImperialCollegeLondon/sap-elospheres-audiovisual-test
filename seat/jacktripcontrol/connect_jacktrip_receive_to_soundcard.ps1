$cached_ip_path=[Environment]::GetEnvironmentVariable("JTC_REMOTE_IP_SETTING", "User")

"Getting IP address of remote machine"
$remote_ip = Get-Content -Path $cached_ip_path
"remote:" + $remote_ip

# connect jactrip to local soundcard
& 'C:/Program Files (x86)/Jack/jack_connect.exe' ($remote_ip + ':receive_1') system:playback_1
& 'C:/Program Files (x86)/Jack/jack_connect.exe' ($remote_ip + ':receive_2') system:playback_2
