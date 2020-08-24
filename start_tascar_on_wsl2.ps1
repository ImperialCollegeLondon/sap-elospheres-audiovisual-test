Start-Process -FilePath "wsl" `
  -ArgumentList "tascar_cli /home/alastair/git/ImperialCollegeLondon/sap-elospheres-audiovisual-test/seat/tascar_scenes/01_three_anechoic_sources_native_binaural.tsc" `
  -RedirectStandardError "errors_from_tascar_on_wsl.txt" `
  -RedirectStandardOutput "output_from_tascar_on_wsl.txt"
