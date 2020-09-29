"Launching jackd process on wsl in new terminal window..."
Start-Process -FilePath "wsl" `
  -ArgumentList '-u root jackd -d dummy -p 128'

"Launching jacktrip process on wsl in new terminal window..."
Start-Process -FilePath "wsl" `
  -ArgumentList "-u root jacktrip -s --nojackportsconnect"

"Done...filtered list of running processes should now show jackd and jacktrip"
wsl bash -c 'ps -e | grep "jack"'
$dummy = Read-Host -Prompt 'Press any key to return'
