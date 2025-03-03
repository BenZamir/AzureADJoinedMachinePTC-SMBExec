import argparse
from impacket.dcerpc.v5 import scmr
import transport
from impacket import smb
from impacket.structure import Structure
from smb3 import SMB2_DIALECT_21
from smbconnection import SMBConnection


class SMBEXEC:
    def __init__(self, command, path=None, exeFile=None, copyFile=None, port=445,
                 userCert='', certPass='', serviceName='',
                 remoteBinaryName=None):
        self.__userCert = userCert
        self.__certPass = certPass
        self.__port = port
        self.__command = command


    def run(self, remoteHost):
        stringbinding = r'ncacn_np:%s[\pipe\svcctl]' % remoteHost
        print('StringBinding %s'%stringbinding)
        rpctransport = transport.DCERPCTransportFactory(stringbinding)
        rpctransport.set_dport('445')
        rpctransport.setRemoteHost(remoteHost)
        rpctransport.preferred_dialect(SMB2_DIALECT_21)

        rpctransport.set_certificate(self.__userCert, self.__certPass)

        rpctransport.set_kerberos(True, remoteHost)

        self.doStuff(rpctransport)



    def doStuff(self, rpctransport):

        dce = rpctransport.get_dce_rpc()
        
        try:
            dce.connect()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(str(e))
            sys.exit(1)

        global dialect
        dialect = rpctransport.get_smb_connection().getDialect()

        try:
            unInstalled = False
            s = rpctransport.get_smb_connection()

            dce = rpctransport.get_dce_rpc()
            dce.connect()
            dce.bind(scmr.MSRPC_UUID_SCMR)

            # Open the SCM on the remote machine
            resp = scmr.hROpenSCManagerW(dce)
            scHandle = resp['lpScHandle']
        except:
            print("Exception raised while connecting")

        service_name = "testsvca"

        print(f"Creating a service on the remote machine...")
        command = f'cmd.exe /c {self.__command}'
        try:
            resp = scmr.hRCreateServiceW(dce, scHandle, service_name, service_name, lpBinaryPathName=command)
            serviceHandle = resp['lpServiceHandle']

        # Start the service
            print(f"Starting service {service_name}...")
            scmr.hRStartServiceW(dce, serviceHandle)
            print("Service started successfully. waiting for outout..")
            time.sleep(4)
        except Exception as e:
            if 'ERROR_SERVICE_REQUEST_TIMEOUT' in str(e):
                print("Got expected ERROR_SERVICE_REQUEST_TIMEOUT, Command ran successfully!")
            else:
                print(f"Error: {e}")

        try:
            if serviceHandle:
                # Stop and delete the service
                
                print(f"Stopping and deleting service {service_name}...")
                try:
                    scmr.hRControlService(dce, serviceHandle, scmr.SERVICE_CONTROL_STOP)
                except:
                    print("Service seems already stopped, deleting")
                scmr.hRDeleteService(dce, serviceHandle)
                scmr.hRCloseServiceHandle(dce, serviceHandle)
                print("Service stopped and deleted.")
        except Exception as e:
            print(f"Error cleaning up service: {e}")
        if dce:
            dce.disconnect()



# Process command-line arguments.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Authenticate to remote Azure AD joined machine using certificate and run PSEXEC.')
    parser.add_argument('--usercert',  help='Valid AzureAD certificate (PFX format).', required=True)
    parser.add_argument('--certpass',  help='PFX password.', required=True)
    parser.add_argument('--remoteip', help='IP or name of the remote client.', required=True)
    parser.add_argument('--command', help='Command to run on the remote machine', required=True)

    args = parser.parse_args()

    executer = SMBEXEC(args.command, userCert=args.usercert, certPass=args.certpass)
    executer.run(args.remoteip)
