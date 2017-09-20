#!powershell
# This file is part of Ansible

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#Requires -Module Ansible.ModuleUtils.Legacy
#Requires -Module Ansible.ModuleUtils.CommandUtil

# TODO: add check mode support

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'

$params = Parse-Args $args -supports_check_mode $false

$raw_command_line = Get-AnsibleParam -obj $params -name "_raw_params" -type "str" -failifempty $true
$chdir = Get-AnsibleParam -obj $params -name "chdir" -type "path"
$creates = Get-AnsibleParam -obj $params -name "creates" -type "path"
$removes = Get-AnsibleParam -obj $params -name "removes" -type "path"
$stdin = Get-AnsibleParam -obj $params -name "stdin" -type 'str"'

$raw_command_line = $raw_command_line.Trim()

$result = @{
    changed = $true
    cmd = $raw_command_line
}

Function Test-FilePath($path) {
    # Test-Path/Get-Item fails on files that are locked like C:\pagefile.sys
    # Get-ChildItem -Path -Filter works fine without any performance
    # degredations so use that instead
    $directory = Split-Path -Path $path -Parent
    $filename = Split-Path -Path $path -Leaf

    $file = Get-ChildItem -Path $directory -Filter $filename -Force -ErrorAction SilentlyContinue
    if ($file -ne $null) {
        if ($file -is [Array] -and $file.Count -gt 1) {
            Fail-Json -obj $result -message "found multiple files at path '$path', make sure no wildcards are set in the path"
        }
        return $true
    } else {
        return $false
    }
}

if ($creates -and $(Test-FilePath -path $creates)) {
    Exit-Json @{msg="skipped, since $creates exists";cmd=$raw_command_line;changed=$false;skipped=$true;rc=0}
}

if ($removes -and -not $(Test-FilePath -path $removes)) {
    Exit-Json @{msg="skipped, since $removes does not exist";cmd=$raw_command_line;changed=$false;skipped=$true;rc=0}
}

$command_args = @{
    command = $raw_command_line
}
if ($chdir) {
    $command_args['working_directory'] = $chdir
}
if ($stdin) {
    $command_args['stdin'] = $stdin
}

$start_datetime = [DateTime]::UtcNow
try {
    $command_result = Run-Command @command_args
} catch {
    $result.changed = $false
    try {
        $result.rc = $_.Exception.NativeErrorCode
    } catch {
        $result.rc = 2
    }
    Fail-Json -obj $result -message $_.Exception.Message
}

$result.stdout = $command_result.stdout
$result.stderr = $command_result.stderr
$result.rc = $command_result.rc

$end_datetime = [DateTime]::UtcNow
$result.start = $start_datetime.ToString("yyyy-MM-dd hh:mm:ss.ffffff")
$result.end = $end_datetime.ToString("yyyy-MM-dd hh:mm:ss.ffffff")
$result.delta = $($end_datetime - $start_datetime).ToString("h\:mm\:ss\.ffffff")

If ($result.rc -ne 0) {
    Fail-Json -obj $result -message "non-zero return code"
}

Exit-Json $result
