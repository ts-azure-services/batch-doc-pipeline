import os
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv('./variables.env')

    keyVaultName = os.environ["KEY_VAULT"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = ClientSecretCredential(tenant_id=os.environ['AZURE_TENANT_ID'],
                                        client_id=os.environ['AZURE_CLIENT_ID'],
                                        client_secret=os.environ['AZURE_CLIENT_SECRET'],
                                        )
    client = SecretClient(vault_url=KVUri, credential=credential)
    secretName = "frkey"
    secretValue = os.environ["COG_KEY"]
    print(f"Creating a secret in {keyVaultName} called '{secretName}'....")
    client.set_secret(secretName, secretValue)
