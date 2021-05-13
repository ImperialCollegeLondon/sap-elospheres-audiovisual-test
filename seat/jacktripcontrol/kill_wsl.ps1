#$cached_ip_path=[Environment]::GetEnvironmentVariable("JTC_REMOTE_IP_SETTING", "User")

#function Get-WSL2IPAdrress {
#  return (wsl hostname -I).Trim()
#}
#$client_ip=Get-WSL2IPAdrress


#"Storing IP address of wsl machine: " + $client_ip
#[Environment]::SetEnvironmentVariable("SEAT_POSE_OSC_DEST", $client_ip, "User")
#$env:SEAT_POSE_OSC_DEST=$client_ip
#Set-Item -Path Env:SEAT_POSE_OSC_DEST -Value $client_ip
#Set-Content -Path $cached_ip_path -Value $client_ip

# wsl bash -c 'pkill -f jackd' # didn't work - not permitted




"Killing jackd process on wsl in new terminal window..."
Start-Process -FilePath "wsl" `
  -ArgumentList '-u root pkill -f jackd'
#
#"Launching jacktrip process on wsl in new terminal window..."
#Start-Process -FilePath "wsl" `
#  -ArgumentList "-u root jacktrip -s --nojackportsconnect"
#
#"Done...filtered list of running processes should now show jackd and jacktrip"
#wsl bash -c 'ps -e | grep "jack"'
# $dummy = Read-Host -Prompt 'Press any key to return'
