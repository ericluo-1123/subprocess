[In PC]
1. You can put it in any location and uppack the zip file. For example, suppose it's put in 
e:\fixture-signdev-agent-server-V0.9.2.2

2. Please follow the rule to prepare your device CSR:

Device Cert with unique DevId
------------------------------------
C=TW, O=Acelink, OU=Device, L=VS-1008, CN=<DevId>
Lifetime=99 years

e.g. C=TW, O=Acelink, OU=Device, L=VS-1008, CN=6ed1577cb898823a3bb567786...

3.Execute the fixture server , see the following for example:

[Windows]
Usage: .\fixtureSignAgent_SSL_cfssl.exe -ip=fixture_ip_address -port=port_no -capath=/locaton_of_certificate
Example: .\fixtureSignAgent_SSL_cfssl.exe -ip=192.168.8.18 -port=8080 -capath=.

[Linux]
go to <PATH>/fixture-signdev-agent-server-V0.9.2.2
Usage: ./fixtureSignAgent_SSL_cfssl -ip=fixture_ip_address -port=port_no -capath=/locaton_of_certificate
Example: ./fixtureSignAgent_SSL_cfssl -ip=192.168.8.18 -port=8080 -capath=.
 
