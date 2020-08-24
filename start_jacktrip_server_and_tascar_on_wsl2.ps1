# start stuff running on WSL
Start-Process -FilePath "wsl" `
  -ArgumentList "jackd -d dummy -r48000 -p128" `
  -RedirectStandardError "errors_from_jack_on_wsl.txt"

Start-Process -FilePath "wsl" `
  -ArgumentList "jacktrip -s" `
  -RedirectStandardError "errors_from_jacktrip_on_wsl.txt"

Start-Process -FilePath "wsl" `
  -ArgumentList "tascar_cli /home/alastair/git/ImperialCollegeLondon/amoore1-elospheres-experiments/20200603_3_source_for_unity_sync/05_freefield_array_3src_plus_concentrated_babble_jacktrip.tsc" `
  -RedirectStandardError "errors_from_tascar_on_wsl.txt" `
  -RedirectStandardOutput "output_from_tascar_on_wsl.txt"
