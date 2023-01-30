import os
import json
import pathlib
import re

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# import environment variables
RPC_URL = os.environ.get("RPC_URL")
GRADE = os.environ.get("GRADE")
WALLET = os.environ.get("WALLET")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
PULL_REQUEST_ID = os.environ.get("PULL_REQUEST_ID")
SAT_DEPLOYMENT_ADDRESS = os.environ.get("SAT_DEPLOYMENT_ADDRESS")


# import the SAT ABI
SAT_ABI = json.loads(open(f"{pathlib.Path(__file__).parent.parent.resolve()}/json/sat.json").read())

# create RPC connection
try: web3 = Web3(Web3.HTTPProvider(RPC_URL))
except: 
    try: web3 = Web3(Web3.WebsocketProvider(RPC_URL))
    except: raise ConnectionError
    
# create the admin account with PRIVATE_KEY
operator = web3.eth.account.privateKeyToAccount(PRIVATE_KEY);

# regex extract ETH address from string
    MINT_TO_ADDRESS = re.search(r"0x[0-9a-fA-F]{40}", WALLET).group(0)

    # create contract instance
    sat = web3.eth.contract(Web3.toChecksumAddress(SAT_DEPLOYMENT_ADDRESS), abi=SAT_ABI)
    raw_transaction = sat.functions.mint(
        Web3.toChecksumAddress(MINT_TO_ADDRESS),
        GRADE,
        WALLET,
    ).buildTransaction(
        {
            "from": operator.address,
            "nonce": web3.eth.getTransactionCount(operator.address),
            "gasPrice": web3.eth.gas_price,
            "chainId": 1,
        }
    )

    # sign & broadcast the transaction
    signed_transaction = web3.eth.account.sign_transaction(raw_transaction, private_key=PRIVATE_KEY)
    web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
else:
    raise ValueError("Error occured while minting the SAT")