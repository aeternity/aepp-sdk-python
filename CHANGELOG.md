# Change Log
All notable changes to this project will be documented in this file. This change
log follows the conventions of [keepachangelog.com](http://keepachangelog.com/).

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
