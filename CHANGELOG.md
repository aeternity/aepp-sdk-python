# Change Log

All notable changes to this project will be documented in this file. This change
log follows the conventions of [keepachangelog.com](http://keepachangelog.com/).

## [Unreleased]

## [1.1.2]

### Changed

- Use native transaction by default with the cli
- Default nonce to 1 when the `get_account_by_pubkey` api call fails.
- Use `getpass` to read the password from the promt

### Fixed

- Range check tests for node version comaptibility

## [1.1.1]

### Changed

- Add range check in node version compatibility

## [1.1.0]

### Changed

- CLI default node changed to [sdk-mainnet.aepps.com](https://sdk-mainnet.aepps.com/v2/status)

### Added

- Native transactions for contracts

## [1.0.0]

### Changed

- Encoding of transaction (and other objects) [changed to base64](https://github.com/aeternity/protocol/blob/epoch-v1.0.0/epoch/api/api_encoding.md)

### Removed

- Compatibility with epoch nodes version < [1.0.0](https://github.com/aeternity/epoch/blob/v1.0.0/docs/release-notes/RELEASE-NOTES-1.0.0.md)

## [0.25.0.1]

⚠️ KEYSTORE FORMAT CHANGE INCOMPATIBLE WITH PREVIOUS FORMAT ⚠️

refer to the [documentation](docs/keystore_format_change.md) about how to update existing keystores

### Added

- Support for offline transaction signing
- Native transaction creation for AENS

### Changed

- The keystore json format as been updated to xsalsa-poly1305/argon2id

## [0.25.0.1b1]

### Added

- Support for network_id when signing transactions

### Removed

- Compatibility with epoch nodes version < [0.25.0](https://github.com/aeternity/epoch/blob/v0.25.0/docs/release-notes/RELEASE-NOTES-0.25.0.md)
- Support for .aet tld for aens

## [0.24.0.2]

### Fixed

- Fix for [CVE-2018-18074](https://nvd.nist.gov/vuln/detail/CVE-2018-18074)

## [0.24.0.1]

### Removed

- Compatibility with epoch nodes version < [0.24.0](https://github.com/aeternity/epoch/blob/v0.24.0/docs/release-notes/RELEASE-NOTES-0.24.0.md)

### Notes

- The keystore/JSON format will be deprecated in the next releases

## [0.22.0.1]

### Removed

- Compatibility with epoch nodes version < [0.22.0](https://github.com/aeternity/epoch/blob/v0.22.0/docs/release-notes/RELEASE-NOTES-0.22.0.md)

### Changed

- Change hash prefix separator from `$` to `_`
- KeyPair object renamed to Account
- Rename `wallet` command to `account`
- Refactor command line client structure
- Spend transactions are built natively (not using debug API)

### Added

- TxBuilder object to provide transactions operations
- Add compatibility check before performing operations against a node
- Add `--force` flag to skip compatibility check with the target node
- Add [exponential backoff](https://developers.google.com/drive/api/v3/handle-errors#exponential-backoff) strategy to verify if a transaction has been included in the chain.
- Add `--wait` flag to instruct the client to wait for a transaction to be included in a chain before returning

## [0.21.0.1]

### Removed

- Compatibility with epoch nodes version < 0.21.0

## [0.20.0.2]

### Fixed

- Pypi distributions contains debug messages

## [0.20.0.1]

### Changed

- Use namehash to calculate name commitment hash

### Removed

- Compatibility with epoch v0.18.0

## [0.18.0.6.1]

### Fixed

- Bump release version number

## [0.18.0.6]

### Added

- Option `--private-key` to the `aecli wallet address` command

### Fixed

- Error while printing the result of the spend command (aecli)
- Possible index out of bound error in signing decode function

## [0.18.0.5]

### Added

- Command `chain play` to explore the blocks of the chain automatically
- Function is_valid_hash in signing module

### Fixed

- Name claiming ignores the epoch url and uses always the local chain

### Changed

- Update cryptography library to 2.3 [CVE-2018-10903](https://nvd.nist.gov/vuln/detail/CVE-2018-10903)
- Contract call option return-type changed to mandatory argument in the cli

## [0.18.0.4]

### Changed

- Improve consistency on the output of the command line client

## [0.18.0.3]

### Fixed

- Transitive dependency installation when installing with pip

## [0.18.0.2]

### Added

- Explicit requirement for python > 3.5
- Bundle command line client in the package

## [0.18.0.1]

### Added

- Command line command to claim and inspect names

### Changed

- Replaced module PyCrypto with cryptography (CVE-2018-6594)
- method `get_block_by_height` to `get_key_block_by_height`
- parameter `account_pubkey` is now `account` in API calls

### Removed

- Compatibility with epoch < 0.18.0
- `get_transactions_in_block_range` since has been removed from the API

## [0.15.0.1]

### Removed

- Legacy Swagger file loading
- Compatibility with < 0.15.0

### Changed

- Update compatibility to epoch v0.15.0
- New cli implementation
- Change versioning scheme

## Unreleased [0.14.0-0.1.0]

### Added

- Transaction hash validation

### Changed

- Update to epoch v0.14.0
- Execute linting in CI

### Removed

### Fixed

- Test executions

## [0.13.0-0.1.0]

### Added

- This change log file
- Flake8 linting configuration
- Jenkins configuratio for CI
- Authors are now taken from `AUTHORS`

### Changed

- Switch to curve ed25519 (from secp256k1) to align with Node protocol changes
- Generate basic API directly from Swagger files, also validate input data

### Fixed

- More consistent code examples
