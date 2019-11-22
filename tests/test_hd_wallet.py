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
    expected_address = "ak_2De9RicLgfnYFWWKqcDiqSEoTetyCrKiBjdJqPDb9ViCzkGRE8"
    expected_private_key = "7632d27fd7adccdd8a4b6f1e02028ba6ec6262575a533f3dfb06a7cfe711f1d4a065d306530d7d7fa6b01cf2ef73a04d9d2da98700b3c797f55cc36c9fb89ab0"

    path, child_account = hdwallet.derive_child()
    assert expected_path == path
    assert child_account.address == expected_address
    assert child_account.get_secret_key() == expected_private_key


    expected_path = "m/44'/457'/12'/0'/0'"
    expected_address = "ak_2a5KtTDNooCWxTGJuB5PRjhfeHvuvc6CuySXiwjp3SPpYb1ZeM"
    expected_private_key = "78c4652b9fd2484763f9280b4b3df5802284b2c0bc92a459703ade27ae28d8efcecbc509ae4d242edda112ac10e2d1913c5103d1ff9046d494a08fa6bd12f833"

    path, child_account = hdwallet.derive_child(account_index=12)
    assert expected_path == path
    assert child_account.address == expected_address
    assert child_account.get_secret_key() == expected_private_key
