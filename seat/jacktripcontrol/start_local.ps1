function Get-WSL2IPAdrress {
  return wsl hostname -I
}

$client_ip=Get-WSL2IPAdrress
"client:"
$client_ip

Start-Process -FilePath "C:/Program Files (x86)/Jack/jackd.exe" `
  -ArgumentList "-S -dportaudio -d""ASIO::ASIO4ALL v2"" -r48000 -p128"

# $env:Path="C:\Qt\Tools\mingw730_64\bin;C:\Qt\5.12.3\mingw73_64\bin;C:\Qt\Tools\mingw730_64\bin;C:\Program Files\Oculus\Support\oculus-runtime;C:\Program Files (x86)\Common Files\Oracle\Java\javapath;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\NVIDIA Corporation\NVIDIA NGX;C:\Program Files\NVIDIA Corporation\NVIDIA NvDLISR;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Java\jdk1.8.0_211\bin;C:\Users\alastair\AppData\Local\Android\Sdk\platform-tools;C:\Users\alastair\AppData\Local\Android\Sdk\tools\bin;C:\Program Files\Git\cmd;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\dotnet\;C:\Users\alastair\AppData\Local\Microsoft\WindowsApps;C:\Users\alastair\bin;C:\Program Files\GPAC;C:\ProgramData\Anaconda2;C:\ProgramData\Anaconda2\Scripts;C:\Program Files\CMake\bin;C:\Users\alastair\AppData\Local\atom\bin;%USERPROFILE%\AppData\Local\Microsoft\WindowsApps;C:\Users\alastair\.dotnet\tools;C:\Program Files\openMHA\bin;C:\Qt\Tools\QtCreator\bin"
#
#
# Start-Process -FilePath "C:\gitwin\jacktrip\jacktrip\build-jacktrip-My_jacktrip-Release\release\jacktrip.exe" `
#   -ArgumentList "-c $client_ip --nojackportsconnect" `
#   -WorkingDirectory  "C:\gitwin\jacktrip\jacktrip\build-jacktrip-My_jacktrip-Release"

Start-Process -FilePath "C:\jacktrip_v1.2.1\jacktrip.exe" `
  -ArgumentList "-c $client_ip --nojackportsconnect"
