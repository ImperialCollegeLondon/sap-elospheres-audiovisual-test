$cached_ip_path=[Environment]::GetEnvironmentVariable("JTC_REMOTE_IP_SETTING", "User")

"Getting IP address of remote machine"
$remote_ip = Get-Content -Path $cached_ip_path
"remote:" + $remote_ip

"Starting jack..."
Start-Process -FilePath "C:/Program Files (x86)/Jack/jackd.exe" `
  -ArgumentList "-S -dportaudio -d""ASIO::ASIO4ALL v2"" -r48000 -p128"

"Starting JackTrip..."
Start-Process -FilePath "C:\jacktrip_v1.2.1\jacktrip.exe" `
  -ArgumentList "-c $remote_ip --clientname $remote_ip --nojackportsconnect"
