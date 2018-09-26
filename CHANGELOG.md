# Change Log
All notable changes to this project will be documented in this file. This change
log follows the conventions of [keepachangelog.com](http://keepachangelog.com/).

## [Unreleased]

## [0.22.0.1]

### Removed
- Compatiblity with epoch nodes version < [0.22.0](https://github.com/aeternity/epoch/blob/v0.22.0/docs/release-notes/RELEASE-NOTES-0.22.0.md) 

### Changed
- change hash prefix separator from `$` to `_`

## [0.21.0.1]

### Removed
- Compatiblity with epoch nodes version < 0.21.0

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
- Replaced module PyCrypto with crypthograpy (CVE-2018-6594)
- method `get_block_by_height` to `get_key_block_by_height`
- paramater `account_pubkey` is now `account` in API calls

### Removed
- Compatibility with epoch < 0.18.0
- `get_transactions_in_block_range` since has been removed from the API 


## [0.15.0.1]

### Removed

- Legacy Swagger file loading
- Compatibility with < 0.15.0

### Changed

- Update compatiblity to epoch v0.15.0
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
- Flake8 linting congiguration
- Jenkins configuratio for CI
- Authors are now taken from `AUTHORS`

### Changed
- Switch to curve ed25519 (from secp256k1) to align with Epoch protocol changes
- Generate basic API directly from Swagger files, also validate input data

### Fixed
- More consistent code examples
