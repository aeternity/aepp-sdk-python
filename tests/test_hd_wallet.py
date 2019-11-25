from aeternity.hdwallet import HDWallet

def test_hdwallet_generate_wallet():
    mnemonic = HDWallet.generate_mnemonic()
    assert mnemonic is not None
    hdwallet = HDWallet(mnemonic)
    assert hdwallet.master_key is not None

def test_hdwallet_generate_wallet_without_mnemonic():
    hdwallet = HDWallet()
    assert hdwallet.mnemonic is not None

def test_hdwallet_path_derivation():
    mnemonic = "energy pass install genuine sell enroll wear announce brother marble test cruise"
    hdwallet = HDWallet(mnemonic)

    expected_path = "m/44'/457'/0'/0'/0'"
    expected_address = "ak_anBY5wEamzK1L1L3f4gZr8RrUMEfgSEmRpAJKTETTETA9k6Kp"
    expected_private_key = "40a0dc9b6be8ca58ec3b6773a118f8237092d0b5f3d48d4c08a6cfbde258aa3d4cb307d4f30e35ea50ddf29043f2827d8c129cd7c03d981a9b0cc79703160e17"

    path, child_account = hdwallet.derive_child()
    assert expected_path == path
    assert child_account.address == expected_address
    assert child_account.get_secret_key() == expected_private_key


    expected_path = "m/44'/457'/12'/0'/0'"
    expected_address = "ak_2FZU4teXWLyHWVbvf1ajejzKrcuyXffP4jaoedRDvv579mEjiY"
    expected_private_key = "032374e3b7c11cb2e5dd62a633d13af7de7f231e721b6f797423978e5e4a7faaa4c17e635de2171a515dc4f049b63957ef8778b4b02533f6791554def9ceda97"

    path, child_account = hdwallet.derive_child(account_index=12)
    assert expected_path == path
    assert child_account.address == expected_address
    assert child_account.get_secret_key() == expected_private_key

    expected_path = "m/44'/457'/12'/0'/1'"
    expected_address = "ak_hPd6XVrLFxBGcKwBbeVA3PWNqE5YJk2NrPuUNp9Lp5q4KHvUX"
    expected_private_key = "96bab5642835618383a48bb759d4179dbc9a0e9bbd79424c973cdfa694fc5c485bb5e51e9d1d7fcf3bd17cd7ae3af549addf1dd4fe66365c72757796e47d5639"

    path, child_account = hdwallet.derive_child(account_index=12, address_index=1)
    assert expected_path == path
    assert child_account.address == expected_address
    assert child_account.get_secret_key() == expected_private_key
