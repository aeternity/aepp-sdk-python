from aeternity.hdwallet import generate_mnemonic, generate_wallet

def test_hdwallet_generate_wallet():
    mnemonic = generate_mnemonic()
    _, account = generate_wallet(mnemonic)
    assert account is not None

def test_hdwallet_generate_wallet_without_mnemonic():
    _, account = generate_wallet()
    assert account is not None