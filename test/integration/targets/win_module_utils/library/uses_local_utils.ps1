#!powershell

# use different cases, spacing and plural of 'module' to exercise flexible powershell dialect
#ReQuiReS   -ModUleS    Ansible.ModuleUtils.PowerShellLegacy
#Requires -Module Ansible.ModuleUtils.ValidTestModule

$o = CustomFunction

Exit-Json @{data=$o}
