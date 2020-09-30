"Getting IP address of remote machine"
$client_ip=[Environment]::GetEnvironmentVariable("SEAT_POSE_OSC_DEST", "User")
"client:" + $client_ip

"Starting jack..."
Start-Process -FilePath "C:/Program Files (x86)/Jack/jackd.exe" `
  -ArgumentList "-S -dportaudio -d""ASIO::ASIO4ALL v2"" -r48000 -p128"

"Starting JackTrip..."
Start-Process -FilePath "C:\jacktrip_v1.2.1\jacktrip.exe" `
  -ArgumentList "-c $client_ip --nojackportsconnect"
