from web3 import Web3

BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

contract_address = Web3.to_checksum_address("0x18b2a687610328590bc8f2e5fedde3b582a49cda")

contract_abi = [
    {
        "constant": True,
        "inputs": [{"name": "index", "type": "uint256"}],
        "name": "rounds",
        "outputs": [
            {"name": "epoch", "type": "uint256"},
            {"name": "startTimestamp", "type": "uint256"},
            {"name": "lockTimestamp", "type": "uint256"},
            {"name": "closeTimestamp", "type": "uint256"},
            {"name": "lockPrice", "type": "uint256"},
            {"name": "closePrice", "type": "uint256"},
            {"name": "lockOracleId", "type": "uint256"},
            {"name": "closeOracleId", "type": "uint256"},
            {"name": "totalAmount", "type": "uint256"},
            {"name": "bullAmount", "type": "uint256"},
            {"name": "bearAmount", "type": "uint256"},
            {"name": "rewardBaseCalAmount", "type": "uint256"},
            {"name": "rewardAmount", "type": "uint256"},
            {"name": "oracleCalled", "type": "bool"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

def get_rounds(index):
    web3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    round_data = contract.functions.rounds(index).call()

    return round_data

if __name__ == "__main__":
    index = 298826
    round_data = get_rounds(index)
    print(f"Round Data for index {index}: {round_data}")
