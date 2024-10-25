from web3 import Web3

BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

contract_address = Web3.to_checksum_address("0x18b2a687610328590bc8f2e5fedde3b582a49cda")

contract_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "currentEpoch",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

def get_current_epoch():
    web3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    current_epoch = contract.functions.currentEpoch().call()
    return str(current_epoch)

if __name__ == "__main__":
    epoch = get_current_epoch()
    print(f"Current Epoch: {epoch}")
