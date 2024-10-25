from web3 import Web3

BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

contract_address = Web3.to_checksum_address("0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE")

contract_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "latestRound",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

def get_latest_round():
    web3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    latest_round = contract.functions.latestRound().call()
    return str(latest_round)

if __name__ == "__main__":
    latest_round = get_latest_round()
    print(f"Latest Round: {latest_round}")
