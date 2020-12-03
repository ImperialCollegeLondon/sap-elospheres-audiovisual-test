# Create an environment variable which has the path to a file and create the file
# This file stores an IP address which changes every time Windows restarts
if (-not (Test-Path env:JTC_REMOTE_IP_SETTING)) {
  $remote_ip_setting_file = $env:LOCALAPPDATA + '\JackTripControl\remote_ip'
  $env:JTC_REMOTE_IP_SETTING = $remote_ip_setting_file
  [Environment]::SetEnvironmentVariable('JTC_REMOTE_IP_SETTING',
      $remote_ip_setting_file, 'User')
}
$remote_ip_setting_file = $env:JTC_REMOTE_IP_SETTING
if (-not (Test-Path $remote_ip_setting_file)) {
  New-Item -ItemType file -Force $remote_ip_setting_file
}
