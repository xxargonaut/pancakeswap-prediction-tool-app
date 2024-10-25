from web3 import Web3

BSC_RPC_URL = "https://bsc-dataseed.binance.org/"

contract_address = Web3.to_checksum_address("0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE")

contract_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_roundId", "type": "uint80"}],
        "name": "getRoundData",
        "outputs": [
            {"name": "roundId", "type": "uint80"},
            {"name": "answer", "type": "uint256"},
            {"name": "startedAt", "type": "uint256"},
            {"name": "updatedAt", "type": "uint256"},
            {"name": "answeredInRound", "type": "uint80"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]
def get_round_data(roundId):
    web3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    round_data = contract.functions.getRoundData(roundId).call()
    return round_data

if __name__ == "__main__":
    roundId = 55340232221128654849
    round_data = get_round_data(roundId)
    print(f"Round Data for index {roundId}: {round_data}")
