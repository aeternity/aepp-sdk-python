# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [3.1.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/3.1.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/3.0.1...3.1.0))

### Features
- feat(state-channels): generic messaging and option to add custom error handler ([02efd3b](https://github.com/aeternity/aepp-sdk-python/commit/02efd3b56e608687e28034ec2e0cc5540d37afc6))
- feat: improve cli output in case of errors ([4636311](https://github.com/aeternity/aepp-sdk-python/commit/4636311b669cfff69a8f91a817fb45b562c01656))
- feat(state-channels): add withdraw related states ([5f6fefa](https://github.com/aeternity/aepp-sdk-python/commit/5f6fefa6c035fbe657d1c2c14069967154723a3a))
- feat(state-channels): sign offchain deposit tx ([0a0ed47](https://github.com/aeternity/aepp-sdk-python/commit/0a0ed47db8cc25c609dc2a921c59735e857aeb16))
- feat: support aeternity node fortuna serie ([>= v2.3.0,  < 4.0.0] [2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4)
)
- feat: support call_info for transaction info endpoint ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- feat: improve logging for unsupported node api version ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- feat: add method to get the protocol version of the a node ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- feat: automatically select the correct vm/abi based on protocol number ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- feat: improve error message when a node is not reachable ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- feat(state-channels): websocket ping pong and dependency fix ([0117324](https://github.com/aeternity/aepp-sdk-python/commit/0117324015f889849ef829dd414f922896f43a36))
- feat(cli): add ability to inspect an encoded transaction ([ec95446](https://github.com/aeternity/aepp-sdk-python/commit/ec9544632e375ac94ff1108a43e4e61bc4da4c9b))
- feat(state-channels): added leave and shutdown calls ([2c1a90c](https://github.com/aeternity/aepp-sdk-python/commit/2c1a90c59e1670052d3947b4cadc7a4a384e4e82))
- feat(state-channels): basic message queue and processing ([ff42d54](https://github.com/aeternity/aepp-sdk-python/commit/ff42d54e513c55ca0493ec5badc982bc7fac08bf))
- feat(state-channels): get channel's current offchain state ([4dbc027](https://github.com/aeternity/aepp-sdk-python/commit/4dbc027d2394f4eae7250679db9eb5de328e6f17))
- feat: Add ability to retrieve an account balance at height from the cli ([a13b516](https://github.com/aeternity/aepp-sdk-python/commit/a13b5161c09782ce8f49493244cc559297d0dda5))
- feat: Add human readable formatting for amounts ([a13b516](https://github.com/aeternity/aepp-sdk-python/commit/a13b5161c09782ce8f49493244cc559297d0dda5))
- feat: Pretty print amounts output from cli ([a13b516](https://github.com/aeternity/aepp-sdk-python/commit/a13b5161c09782ce8f49493244cc559297d0dda5))
- feat: Add ability to transfer a percentage of funds to another account ([a13b516](https://github.com/aeternity/aepp-sdk-python/commit/a13b5161c09782ce8f49493244cc559297d0dda5))
- feat(state-channels): added leave and shutdown calls ([db95c42](https://github.com/aeternity/aepp-sdk-python/commit/db95c42310e74f3bdb94570dd0774fafef650df0))
- feat(state-channels): basic implementation for websocket connection, channel initialization and fetch account balance ([2544aa0](https://github.com/aeternity/aepp-sdk-python/commit/2544aa0f8e0d9335657f87d65c9e4b43d67d2a84))
### Style
- style: fix spell mistakes ([4636311](https://github.com/aeternity/aepp-sdk-python/commit/4636311b669cfff69a8f91a817fb45b562c01656))
- style(state-channels): remove blank lines ([151d48a](https://github.com/aeternity/aepp-sdk-python/commit/151d48ad7ed919c18aae5cd5ced299975dbc5d5f))
- style: fix linting issue ([2a696ba](https://github.com/aeternity/aepp-sdk-python/commit/2a696ba0ef54fe6a49ea4d8d72393201ae1704e4))

### Code refactoring
- refactor(state-channels): use single quotes wherever possible ([7910e21](https://github.com/aeternity/aepp-sdk-python/commit/7910e2117df66e8c0f85ccb6712716a6ec87b976))
- refactor(state-channels): refactor get channel id ([a08fa47](https://github.com/aeternity/aepp-sdk-python/commit/a08fa4744f25fce1dc6a055b1581258061bbc747))
- refactor: update websocket dependencies ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- refactor(state-channels): refactor for balances call ([3cde14d](https://github.com/aeternity/aepp-sdk-python/commit/3cde14d9cfc9087e608ae4c58f70202093b74a63))

### Bug Fixes
- fix(state-channels): add shutdown tx signing ([f2726d8](https://github.com/aeternity/aepp-sdk-python/commit/f2726d86a33dc0f7d84d33c7e64a62fcec56d4a3))
- fix(state-channels): Fix channel shutdown. add shutdown tx signing ([3d82bd6](https://github.com/aeternity/aepp-sdk-python/commit/3d82bd6e65d5db2db303ea58da9f9ae7d3601bb7))
- fix: validator check on aens with uppercase letters ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- fix(state-channels): run websocket connection as background task ([072cf55](https://github.com/aeternity/aepp-sdk-python/commit/072cf552b6e9a699fe2e5b362017b8d8988baf16))
- fix(state-channels): updated to more stable websockets library ([2f98467](https://github.com/aeternity/aepp-sdk-python/commit/2f98467c780c2e9831436f5451adbf4988aa10ca))
- fix(state-channels): fix websocket connection crash issue ([4dbba3a](https://github.com/aeternity/aepp-sdk-python/commit/4dbba3ac31228d6f79d5a63d32a06f10add9e783))

### Build
- build: switch from setup.py to pyproject.toml (and poetry) ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))
- build: add flake8 configuration to skip unnecessary folders ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))

### Chore
- chore: Removed legacy submodule ([a13b516](https://github.com/aeternity/aepp-sdk-python/commit/a13b5161c09782ce8f49493244cc559297d0dda5))

### Documentation
- docs(state-channels): add comments to the state method ([371ff54](https://github.com/aeternity/aepp-sdk-python/commit/371ff5480367cec29b1cb053a0e030f16137ab4f))
- doc: update readme ([4636311](https://github.com/aeternity/aepp-sdk-python/commit/4636311b669cfff69a8f91a817fb45b562c01656))
- doc: add github badges to the readme ([2191eae](https://github.com/aeternity/aepp-sdk-python/commit/2191eae3d649412d95e39cb25328ff1b0bf8cfc4))


## [3.0.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/3.0.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/2.0.0...3.0.0))
## [3.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/3.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/3.0.0...3.0.1))

### Bug Fixes
- fix: openapi parser for node v2.4.0 (#157) ([63b46fa](https://github.com/aeternity/aepp-sdk-python/commit/63b46faede29e1fa3556a59e3657184a6a59a290)).


## [3.0.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/3.0.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/2.0.0...3.0.0)) - 2019-04-16

### Bug Fixes
- fix: honour value of transaction fee provided as parameter ([d525aba](https://github.com/aeternity/aepp-sdk-python/commit/d525aba38dab3e4c22b596d229a8975f01183c59)). Related issues/PRs: #128

### Code Refactoring
- refactor: add get_secret_key method (deprecates get_private_key) ([8516443](https://github.com/aeternity/aepp-sdk-python/commit/85164432b4f0b48a03cba89e038547c69eba13cc)).
- refactor: set the minimum fee when the provided fee is 0 ([99a3c0f](https://github.com/aeternity/aepp-sdk-python/commit/99a3c0fb67b5349cfa1f4d0fca420f8842dfa984)). Related issues/PRs: #128

### Features
- feat(cli): add payload to the account spend command ([7cdf2d9](https://github.com/aeternity/aepp-sdk-python/commit/7cdf2d917dd5b1e35e20ab04a2a9716d7c19e1a9)). Related issues/PRs: #104
- feat: add support for sofia and raw encoding of account address ([fb6fea6](https://github.com/aeternity/aepp-sdk-python/commit/fb6fea601609738b822d4549e3bcc6f4df99f04b)). Related issues/PRs: #134

### Misc
- ci(node): set the docker node image version to 2.1.0 ([37696fa](https://github.com/aeternity/aepp-sdk-python/commit/37696fafbe816d3f057d2ecb9c99f3134098f0df)).
- Feature/cli sp37 iteraction (#146) ([da645a5](https://github.com/aeternity/aepp-sdk-python/commit/da645a5500643f8ea3bae1f1c34836f67e4a59d9)).
- Feature/new compiler (#145) ([8b4853a](https://github.com/aeternity/aepp-sdk-python/commit/8b4853a182f55a905a18f3029e0472df3ba1063e)).
- Merge pull request #137 from aeternity/fix/cli_fee_param ([0ea6817](https://github.com/aeternity/aepp-sdk-python/commit/0ea6817969b2b2344af3628366150025f0d18096)).
- Merge pull request #138 from aeternity/feature/cli_spend_payload ([cbee5e0](https://github.com/aeternity/aepp-sdk-python/commit/cbee5e072a757886ffde2d90962827d58a055623)).
- Merge pull request #139 from aeternity/feature/contracts_address_format ([51597af](https://github.com/aeternity/aepp-sdk-python/commit/51597af28e2f12f81106f9757eeb51c4e4847c6f)).
- Merge pull request #147 from aeternity/release/3.0.0 ([7dc3a2f](https://github.com/aeternity/aepp-sdk-python/commit/7dc3a2f6aae42e63c197341b7f37dd80345248be)).
- style: fix lint errors ([519f66c](https://github.com/aeternity/aepp-sdk-python/commit/519f66c2e4e0a452474de22ca62b1d3fe70db4ff)).
- update version to 3.0.0 ([c7e59ac](https://github.com/aeternity/aepp-sdk-python/commit/c7e59acd1a027960cb2efd68d0ed2d43e891636c)).


## [2.0.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/2.0.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/1.1.2...2.0.0)) - 2019-03-05

### Misc
- Add generic signautre verification (#109) ([6fa956a](https://github.com/aeternity/aepp-sdk-python/commit/6fa956abcbc70d8a5741a4a45a26d601943c211d)).
- Change reference from Epoch to Aeternity Node (#107) ([c3d7e6c](https://github.com/aeternity/aepp-sdk-python/commit/c3d7e6c1490a6f9e51c71cba8c86f2ef40549799)).
- Chore/general cleanup and fixes (#108) ([d97894e](https://github.com/aeternity/aepp-sdk-python/commit/d97894ea689ffeebe14c2628adbbd15610b73e4f)).
- Feature/node 2.0.0 (#112) ([1986de6](https://github.com/aeternity/aepp-sdk-python/commit/1986de697df3b0773037932da9818e964c4932a0)).
- Feature/tx decoding (#117) ([b7c60dc](https://github.com/aeternity/aepp-sdk-python/commit/b7c60dc569c15e985edfc77588a726c8e83e5f8d)).
- Feature/update docs (#98) ([223747f](https://github.com/aeternity/aepp-sdk-python/commit/223747fb5267d78a23aa65ad79ffb295597d82e9)).
- Improve command line output ([7bf0ef5](https://github.com/aeternity/aepp-sdk-python/commit/7bf0ef54d1823c628f4e0282825daacb7cef750a)).
- Merge branch 'master' into develop ([302c8ec](https://github.com/aeternity/aepp-sdk-python/commit/302c8eca9b3422418d0ed3311ca7d62c00ec0cd6)).
- Merge pull request #118 from aeternity/release/v2.0.0 ([1dca16f](https://github.com/aeternity/aepp-sdk-python/commit/1dca16f194cdc6cbb64dcee3c3996036cd6b0ad1)).
- Remove personal notes from env file ([71604a4](https://github.com/aeternity/aepp-sdk-python/commit/71604a44ff9f1b0277d1b8b63ec5dd8c9452f541)).
- Update changelog and verision number ([c7163f5](https://github.com/aeternity/aepp-sdk-python/commit/c7163f5f0c2ee10a926284cdfb72f579a2158181)).
- Update README.md ([73eed3f](https://github.com/aeternity/aepp-sdk-python/commit/73eed3ff8efa2455aa5c86384df896b164c2572a)).


## [1.1.2](https://github.com/aeternity/aepp-sdk-python/releases/tag/1.1.2) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/1.1.1...1.1.2)) - 2018-12-14

### Misc
- Feature/swagger openapi version check (#94) ([405d7dd](https://github.com/aeternity/aepp-sdk-python/commit/405d7ddd0a39bf889303f5660098a55e9754518d)).
- Hotfix/defalut native tx (#96) ([627c627](https://github.com/aeternity/aepp-sdk-python/commit/627c627225d42337e46ba228b574facddc012bf4)).


## [1.1.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/1.1.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/1.1.0...1.1.1)) - 2018-12-01

### Misc
- Implement range check for epoch compatibility (#91) ([3444256](https://github.com/aeternity/aepp-sdk-python/commit/34442569fea77aec3e1c7e9d1c65ae719bdb234c)).
- Merge pull request #92 from aeternity/release/1.1.1 ([d034d46](https://github.com/aeternity/aepp-sdk-python/commit/d034d4671db9e5841cf66085dd8d117d025d279e)).
- Update version to 1.1.1 and update changelog ([5d1cced](https://github.com/aeternity/aepp-sdk-python/commit/5d1cced0a080011e285dbb923e1daec3f41d458b)).


## [1.1.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/1.1.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/1.0.0...1.1.0)) - 2018-11-29

### Misc
- Feature/native contracts transactions (#88) ([c17ee71](https://github.com/aeternity/aepp-sdk-python/commit/c17ee71c567aa59a1757ad5309717f7d4e4c9a57)).
- Fix and update changelog ([53700e9](https://github.com/aeternity/aepp-sdk-python/commit/53700e9b07a03bac2bb1eeb01ebd6d21e2d127c1)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([4cd2b90](https://github.com/aeternity/aepp-sdk-python/commit/4cd2b908912cb75a87b8cc3d020d45283b2c700d)).
- Merge pull request #89 from aeternity/release/1.1.0 ([79a3a0a](https://github.com/aeternity/aepp-sdk-python/commit/79a3a0a10608bfb3224f9ada510497e2d26051d7)).
- Update sdk version to 1.1.0 ([a2478a4](https://github.com/aeternity/aepp-sdk-python/commit/a2478a42828e8a6ec0a679455ac8f2060acf1a58)).
- Use sdk-mainnet as default node ([5e1234c](https://github.com/aeternity/aepp-sdk-python/commit/5e1234cce1a836e0cbd156463901bab7fa650859)).


## [1.0.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/1.0.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.25.0.1...1.0.0)) - 2018-11-28

### Misc
- Feature/epoch 1.0.0 (#86) ([171c26b](https://github.com/aeternity/aepp-sdk-python/commit/171c26bef3afe717d5d58f8e4d01ae7989baeb66)).
- Feature/oracles (#84) ([1004e9f](https://github.com/aeternity/aepp-sdk-python/commit/1004e9f73a4c7744ee2fa4e45f4ff9ad14ffe3b4)).
- Merge branch 'master' into develop ([60892bc](https://github.com/aeternity/aepp-sdk-python/commit/60892bc54d2c8aef37387f404df82752296d1f9d)).
- Merge pull request #87 from aeternity/release/1.0.0 ([e320c4e](https://github.com/aeternity/aepp-sdk-python/commit/e320c4eacedf347f39b5aeb90d542e8778dae4c4)).
- Update version number to 1.0.0 ([fe8cae4](https://github.com/aeternity/aepp-sdk-python/commit/fe8cae4e87f870e85eef47da03db88443ef575bf)).


## [0.25.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.25.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.25.0.1b1...0.25.0.1)) - 2018-11-23

### Misc
- Add DEBUG environment variable to README ([0ae8c18](https://github.com/aeternity/aepp-sdk-python/commit/0ae8c181726b28a6c5ee7f51da877635f25c15b2)).
- Add github issues template ([348aad2](https://github.com/aeternity/aepp-sdk-python/commit/348aad2fe35618555ddd44e2c821fba0c6dd57a4)).
- Change command options order (#81) ([c9a08eb](https://github.com/aeternity/aepp-sdk-python/commit/c9a08eb8d270ffb525d8fa4f2eec054e75771c33)).
- correction of README.md ([6c863ff](https://github.com/aeternity/aepp-sdk-python/commit/6c863ff758c97bf8cc116a3f9a0c0aeb0cbd8375)).
- Feature/native_aens_tx (#77) ([1fd8199](https://github.com/aeternity/aepp-sdk-python/commit/1fd81998092c84a1013b0a074b0982a2a38c794a)).
- Feature/offline (#79) ([a1c84d8](https://github.com/aeternity/aepp-sdk-python/commit/a1c84d87622ed10e3b65820f774910f72f96b3f0)).
- Fix offline signing Improve support for network_id ([c36a91d](https://github.com/aeternity/aepp-sdk-python/commit/c36a91d0f239f842f164d4f749c0969386f20162)).
- Fix typos ([c05524f](https://github.com/aeternity/aepp-sdk-python/commit/c05524f5ada2fbe7a9780d204f0b478e266f6e53)).
- Fix typos in md files ([309e832](https://github.com/aeternity/aepp-sdk-python/commit/309e832490d14c3689eaa31a065bd286b5067bdc)).
- Merge branch 'master' into develop ([df1745a](https://github.com/aeternity/aepp-sdk-python/commit/df1745a4b47be5153c7cf745e9b4265ce255f3e2)).
- Merge branch 'release/0.25.0.1' of github.com:aeternity/aepp-sdk-python into release/0.25.0.1 ([a749c4d](https://github.com/aeternity/aepp-sdk-python/commit/a749c4d9442442415e7e665d8aa3c7c9fe9f3855)).
- Merge pull request #80 from aeternity/release/0.25.0.1 ([58848ce](https://github.com/aeternity/aepp-sdk-python/commit/58848ce7f8aa6cb2ffee40f1865b71eee8fd0ac4)).
- Remove tests keys ([ee92ad8](https://github.com/aeternity/aepp-sdk-python/commit/ee92ad8f93c0bdd9bb63fe591bd0189a43ba6298)).
- Removed commented code ([08f925e](https://github.com/aeternity/aepp-sdk-python/commit/08f925e3036e78f1500747eba400225949c1d65e)).
- Set native default to False Give better output for inspect blocks ([db70663](https://github.com/aeternity/aepp-sdk-python/commit/db706630f5d1e8386b753a64647f70963f339380)).
- Update changelog and documentation ([b43ec74](https://github.com/aeternity/aepp-sdk-python/commit/b43ec74b17849d144856f355dea7c8604385a602)).
- Update verison to 0.25.0 ([9d2e3c6](https://github.com/aeternity/aepp-sdk-python/commit/9d2e3c6c9d1abed6630498f6b234354fd2a6141f)).
- xsalsa-poly1305 ([87893e1](https://github.com/aeternity/aepp-sdk-python/commit/87893e136efa461f2eec4277fc5647054b2c1c8e)).


## [0.25.0.1b1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.25.0.1b1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.24.0.2...0.25.0.1b1)) - 2018-11-06

### Misc
- Feature/epoch 0.25.0 (#72) ([1b06da0](https://github.com/aeternity/aepp-sdk-python/commit/1b06da057ec5bd29cd5d893eb82b6bc6223db606)).
- Merge pull request #73 from aeternity/release/0.25.0.1b1 ([22e7795](https://github.com/aeternity/aepp-sdk-python/commit/22e77952a1666d67b4dc2094b92fd33a3089f114)).
- Update changelog ([6f3ee1b](https://github.com/aeternity/aepp-sdk-python/commit/6f3ee1beadeaf4fd71a9aaa714d54c4d027b2d7d)).


## [0.24.0.2](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.24.0.2) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.24.0.1...0.24.0.2)) - 2018-11-01

### Misc
- Feature/sonar (#68) ([ee224e3](https://github.com/aeternity/aepp-sdk-python/commit/ee224e38d4b2553767a98da851eb29d91f45b205)).
- Fix for CVE-2018-18074  (#69) ([c5e6a36](https://github.com/aeternity/aepp-sdk-python/commit/c5e6a3618eeeb558c3d4ca349d26766891f60707)).
- Merge branch 'master' into develop ([76c11b1](https://github.com/aeternity/aepp-sdk-python/commit/76c11b197c9ce3e7ca3b2c092eb5b20daf00ed6f)).
- Merge pull request #70 from aeternity/release/0.24.0.2 ([bce24f0](https://github.com/aeternity/aepp-sdk-python/commit/bce24f0c1db43e9ddf2d2d5b6495ca644c0fa299)).
- Update version and changelog ([bd7fa6d](https://github.com/aeternity/aepp-sdk-python/commit/bd7fa6d816d2b13326ebbdf4814cb4a414096571)).


## [0.24.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.24.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.24.0.1b1...0.24.0.1)) - 2018-10-19

### Misc
- Merge branch 'master' into develop ([444aa8c](https://github.com/aeternity/aepp-sdk-python/commit/444aa8cba45872c3600d22ed6b815cb0399768ee)).
- Release/0.24.0.1 (#64) ([2c6e215](https://github.com/aeternity/aepp-sdk-python/commit/2c6e215aee4b524c7bd11268b33c4be726aa27f3)).
- Release/0.24.0.1 (#67) ([35ef090](https://github.com/aeternity/aepp-sdk-python/commit/35ef090416522ef91873a71c0978d4e9f04b45c2)).


## [0.24.0.1b1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.24.0.1b1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.22.0.1...0.24.0.1b1)) - 2018-10-19

### Misc
- Merge from master ([247f98e](https://github.com/aeternity/aepp-sdk-python/commit/247f98e7ca98564a0a35ad7919b8759b03a1dc8d)).
- Release/0.24.0.1b1 (#63) ([031bf48](https://github.com/aeternity/aepp-sdk-python/commit/031bf48e532848b99b063af9ae1dfdcafb254423)).


## [0.22.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.22.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.22.0.1rc2...0.22.0.1)) - 2018-10-18

### Misc
- Chore/spend transaction (#58) ([edc999e](https://github.com/aeternity/aepp-sdk-python/commit/edc999e1b3354503b7c9772c84b1e6c1831ed1dd)).
- Feature/cli_compliance (#60) ([6ee14a1](https://github.com/aeternity/aepp-sdk-python/commit/6ee14a1abc8d5109b660f08f951aa7c4bd07bea5)).
- Feature/epoch-0.24.0 (#62) ([87853fb](https://github.com/aeternity/aepp-sdk-python/commit/87853fbb2ca90ab57a15a36329099aaf8b145ef9)).
- Feature/keystore json (#55) ([2ab15d6](https://github.com/aeternity/aepp-sdk-python/commit/2ab15d6f3e052731fb84107ff1e822376e9942c4)).
- Feature/native transactions (#56) ([3a08f31](https://github.com/aeternity/aepp-sdk-python/commit/3a08f311dad524979c6dee57f9e46a8d8e9f19a6)).
- Feature/output json (#54) ([03b3f18](https://github.com/aeternity/aepp-sdk-python/commit/03b3f18e23e451afb45b1941afe2a9aed5b64781)).
- Merge pull request #61 from aeternity/release/0.22.0.1 ([dc90b6e](https://github.com/aeternity/aepp-sdk-python/commit/dc90b6e8a8660a6885066de1678235787f776eeb)).
- Remove unnecessary libraries from the setup.py ([8300496](https://github.com/aeternity/aepp-sdk-python/commit/83004961406133b6540512a110b4fc1bcd741fcf)).
- Update command-line-tool.md (#57) ([d140c38](https://github.com/aeternity/aepp-sdk-python/commit/d140c380f2ed1c5c9de6223f93d649d5dad8eead)).
- Update version number to 0.22.0.1 and Changelog ([dc81c49](https://github.com/aeternity/aepp-sdk-python/commit/dc81c4914ea0f6147466478eb03dc17b6cc85e57)).


## [0.22.0.1rc2](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.22.0.1rc2) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.22.0.1rc1...0.22.0.1rc2)) - 2018-10-02

### Misc
- Add epoch version compatibility check (#51) ([b4c32d0](https://github.com/aeternity/aepp-sdk-python/commit/b4c32d0718c7b21cae276441557b02b1df7be909)).
- Feature/calculate_nonce (#50) ([8960d17](https://github.com/aeternity/aepp-sdk-python/commit/8960d17646f384adfed90f3794854222fc7ce76c)).
- Feature/tx execution reliability (#52) ([8d30f58](https://github.com/aeternity/aepp-sdk-python/commit/8d30f586391c798e9ecac053d73e0a15e8db65a4)).
- Hotfix - forgot to increase version number ([d20564a](https://github.com/aeternity/aepp-sdk-python/commit/d20564a6a6c0f3346e7388852c3be69f1d916005)).
- Merge branch 'master' into release/0.22.0.1rc2 ([5d242a2](https://github.com/aeternity/aepp-sdk-python/commit/5d242a28cf1397abed0f31cbc022827f4681253c)).
- Merge pull request #53 from aeternity/release/0.22.0.1rc2 ([2b2db85](https://github.com/aeternity/aepp-sdk-python/commit/2b2db854c923aedbc28e87e8642970902de92571)).
- Update changelog ([a6343b9](https://github.com/aeternity/aepp-sdk-python/commit/a6343b9bff1663e7256826c55b97a773b05ca949)).


## [0.22.0.1rc1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.22.0.1rc1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.20.0.2...0.22.0.1rc1)) - 2018-09-26

### Misc
- Feature/epoch 0.21.0 (#47) ([47466ef](https://github.com/aeternity/aepp-sdk-python/commit/47466ef49481ba1b4607a6267c06e872cfe2c3d2)).
- Feature/epoch-0.22.0 (#48) ([13fa8c3](https://github.com/aeternity/aepp-sdk-python/commit/13fa8c30777be00c149965248ce62a56088a95ae)).
- Merge pull request #49 from aeternity/release/0.22.0.1rc1 ([ea6fc22](https://github.com/aeternity/aepp-sdk-python/commit/ea6fc22a5d66469e8fe3cc03c6fc8a1dff7cd17c)).


## [0.20.0.2](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.20.0.2) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.20.0.1...0.20.0.2)) - 2018-09-05

### Misc
- Bump version to 0.20.0.2 ([e52b790](https://github.com/aeternity/aepp-sdk-python/commit/e52b790d0320a3e4af3cfce9531c453dc4e73a75)).
- Merge pull request #46 from aeternity/hotfix/pypi-dist ([627c529](https://github.com/aeternity/aepp-sdk-python/commit/627c529b0c69837d1af7e27863f6ff43ffd08af1)).


## [0.20.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.20.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.6.1...0.20.0.1)) - 2018-08-23

### Misc
- Add automated deploy to pypi ([2a745a4](https://github.com/aeternity/aepp-sdk-python/commit/2a745a46c84baa8ede2f28c10ebeb0c45a93d805)).
- Automatically publish on test.pypi.org on develop branch Automatically publish on pypi.org on tags ([7aab3fb](https://github.com/aeternity/aepp-sdk-python/commit/7aab3fb21b7f574357f40d1f847e02537c1b1981)).
- Bump version to 0.20.0.1 Update epoch reference version 0.20.0 Use namehash to calculate the commitment hash Update changelog ([d8b0433](https://github.com/aeternity/aepp-sdk-python/commit/d8b0433b5bc274b12fef8643ac5116bf56503a98)).
- Increase default ttl from 10 to 100 Set the name_ttl to 100 in tests ([c99d0e3](https://github.com/aeternity/aepp-sdk-python/commit/c99d0e3a71b31dc48028fd4a7ee90415570b6ff8)).
- merge master into develop ([e385442](https://github.com/aeternity/aepp-sdk-python/commit/e385442005409a05529501b1eaf56050727e3b3e)).
- Merge pull request #42 from aeternity/feature/epoch-0.20.0 ([042c705](https://github.com/aeternity/aepp-sdk-python/commit/042c70558406e41ef07ff9f3541f00b5c69b5eca)).
- Merge pull request #43 from aeternity/release/0.20.0.1 ([dff2cf3](https://github.com/aeternity/aepp-sdk-python/commit/dff2cf3d18af7a5cb880c9cf01dabd56f4b1db7e)).
- Set the target epoch version 0.20.0 for tests ([bfc5f4e](https://github.com/aeternity/aepp-sdk-python/commit/bfc5f4eb5d925576397bee34b675f3bae62ddf6e)).


## [0.18.0.6.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.6.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.6...0.18.0.6.1)) - 2018-08-15

### Misc
- Release/0.18.0.6.1 (#41) ([c14ba6e](https://github.com/aeternity/aepp-sdk-python/commit/c14ba6e2b135915c81f0777e3356dfb2877d5ab6)).


## [0.18.0.6](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.6) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.5...0.18.0.6)) - 2018-08-15

### Misc
- Add --private-key options to the cli to print the private key as a string Fix output print for the spend transaction ([6146bed](https://github.com/aeternity/aepp-sdk-python/commit/6146bedc57e39ef687c45dbe9ac501a99b4360dc)).
- Fix possible index out of range in signing decode function ([809da32](https://github.com/aeternity/aepp-sdk-python/commit/809da322b94fcddd5c0f66cb8845bd4e8bee8021)).
- merge 0.18.0.5 into develop ([81305dd](https://github.com/aeternity/aepp-sdk-python/commit/81305dd6b21548cbe7fbe4388d5a2fc4a1c4d07c)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([1c04df5](https://github.com/aeternity/aepp-sdk-python/commit/1c04df579abe3f18a8199ea33d90e1a672accc34)).
- Release/0.18.0.6 (#40) ([9999b45](https://github.com/aeternity/aepp-sdk-python/commit/9999b4558ad6e508c91eee2d3ae811afec74bdf0)).
- Update changelog ([214c1a1](https://github.com/aeternity/aepp-sdk-python/commit/214c1a192ecf155f462c73557f5b5ee2105fc505)).
- Update command-line-tool.md ([fa68f70](https://github.com/aeternity/aepp-sdk-python/commit/fa68f70289318a08823c3b8ca429c0bd0946bd68)).


## [0.18.0.5](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.5) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.4...0.18.0.5)) - 2018-08-14

### Misc
- Command line tool documentation and examples corrected ([4b61896](https://github.com/aeternity/aepp-sdk-python/commit/4b61896959a7ae3fe173ce8088c930c83b4daad1)).
- Command line tool documentation and examples updated ([f0db8e8](https://github.com/aeternity/aepp-sdk-python/commit/f0db8e8d6a7447ae20dffabe261013f1e77074b3)).
- Create index.md ([c613921](https://github.com/aeternity/aepp-sdk-python/commit/c613921d06f19ef0633021f10689786bfb21e0b6)).
- Decode the result of a contract using the decode-data api call Crate a descriptor of a contract deploy so the client doesnt have to compile a contract over and over Contracts get complied when the object get instantiated if the bytecode is not provided on the constructor ([5af7884](https://github.com/aeternity/aepp-sdk-python/commit/5af7884045d85c3e99d6458e133ab0c4e96ad0e5)).
- Feature/add name commands (#36) ([89229c1](https://github.com/aeternity/aepp-sdk-python/commit/89229c1f28c6c5787e287a27e9a3371497c66a1d)).
- Feature/validate aet hash (#38) ([fbffb39](https://github.com/aeternity/aepp-sdk-python/commit/fbffb3939c8039dac08940d6def22999da6a9494)).
- Fix duplicate function signature ([52686b5](https://github.com/aeternity/aepp-sdk-python/commit/52686b5f5cb3940255bb75b4cbe7bc2489c1bdd8)).
- Fix lint error ([21bcebf](https://github.com/aeternity/aepp-sdk-python/commit/21bcebf1d19b2245593c34dae3089218a879c4f1)).
- Hotfix/claim (#33) ([40c76fe](https://github.com/aeternity/aepp-sdk-python/commit/40c76fe25657a4a99d767eb16c06fad2027405ba)).
- Implement the command play that ([f989de1](https://github.com/aeternity/aepp-sdk-python/commit/f989de1548d45bc4dcee8cf3ece3411b1adea1eb)).
- Inpect of a deploy desciptor prints also informations about the transaction of the contract cration ([757e984](https://github.com/aeternity/aepp-sdk-python/commit/757e98491979c9e60150ab3fa6559aa46c577b91)).
- Make a Contract object store the values of a contract: bytecode, source code and contract address. Increase default gas for contracts in CLI Uses the full contract address in the deploy descriptor name Changed author to owner in the deploy descriptor ([6396acb](https://github.com/aeternity/aepp-sdk-python/commit/6396acbde58e6a153e7da503181c34d7d79f8fbd)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([70d1b12](https://github.com/aeternity/aepp-sdk-python/commit/70d1b1242d6fed5d7ab4c5d940042db1a969b412)).
- Merge pull request #34 from aeternity/feature/chain_play ([b73e50c](https://github.com/aeternity/aepp-sdk-python/commit/b73e50c2b85a0217a43cc3f58690d7911dc8ee5e)).
- Merge pull request #35 from aeternity/feature/data_decode ([a279f63](https://github.com/aeternity/aepp-sdk-python/commit/a279f63bc530030891e494029b17408b0f6811d8)).
- Merge remote-tracking branch 'origin/develop' into feature/chain_play ([a8e6d9f](https://github.com/aeternity/aepp-sdk-python/commit/a8e6d9f5824f1cc4ea78789083a4f289094dec37)).
- Play command (#37) ([3245b8b](https://github.com/aeternity/aepp-sdk-python/commit/3245b8b25faf3a608b4b4d1696e8ff9daf9fa2bd)).
- Print 'N/A' for variable that are None in cli output Handle the transaction not found error gracefully ([76bd26a](https://github.com/aeternity/aepp-sdk-python/commit/76bd26a8a5282b442caba6640c88ef78e8d8e92d)).
- Refactor contract code to handle the contract address and abi more consistently ([1151f52](https://github.com/aeternity/aepp-sdk-python/commit/1151f52e6ae4154efce9a30dfaacb8ddef264305)).
- Release/0.18.0.5 (#39) ([bb96f56](https://github.com/aeternity/aepp-sdk-python/commit/bb96f56b619435a03f5cbc2f27e8782ce9e34610)).
- Resolve conflict in imported libraries ([c5e5454](https://github.com/aeternity/aepp-sdk-python/commit/c5e545451317f14049c49acfd77af17486436342)).
- Started documentation of command line tool ([66f9d60](https://github.com/aeternity/aepp-sdk-python/commit/66f9d60e758040878e2e1b49a67f24ff14eaa38a)).
- Update changelog with the play command ([ecdddce](https://github.com/aeternity/aepp-sdk-python/commit/ecdddce5242d10e87fd165bc0b42b9bede32e592)).
- Update command-line-tool.md ([0990ded](https://github.com/aeternity/aepp-sdk-python/commit/0990dedd2b00e84c43e6a5727d9cb2e7b122c7e3)).
- Update index.md ([f9a9da6](https://github.com/aeternity/aepp-sdk-python/commit/f9a9da642ad0ca9823674aaae0f20b634aab277d)).
- Update test for contracts, add the decode_data test ([baa5653](https://github.com/aeternity/aepp-sdk-python/commit/baa56535e773889585e92cfeb16a31848b48af60)).
- updates ([d4ca6c5](https://github.com/aeternity/aepp-sdk-python/commit/d4ca6c55a0474cb925f7d30b46e08901499ad0e2)).
- Use ip address 127.0.0.1 instead of localhost to connect to docker ([b600d11](https://github.com/aeternity/aepp-sdk-python/commit/b600d1164aed9dafef76c4aed51e8ad16b82d86c)).


## [0.18.0.4](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.4) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.3...0.18.0.4)) - 2018-07-31

### Misc
- Feature/cli changes (#32) ([656f091](https://github.com/aeternity/aepp-sdk-python/commit/656f09176381669371b415f53bf04bb55f2f8b73)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([310d190](https://github.com/aeternity/aepp-sdk-python/commit/310d1909d38048f61fe43d8857c8b30f4babbc26)).
- Merge branch 'master' into develop ([eb7337c](https://github.com/aeternity/aepp-sdk-python/commit/eb7337c52ce4544bf0f5f584240437afe8de61ef)).
- Merged with master ([68d6400](https://github.com/aeternity/aepp-sdk-python/commit/68d640077ff18469a173f5034686c7642bf9b1ee)).
- Merged with master ([fa73d2f](https://github.com/aeternity/aepp-sdk-python/commit/fa73d2fbafea18e344ed5e8ffa392903e31cb29c)).
- Release 0.18.0.4 ([e27032e](https://github.com/aeternity/aepp-sdk-python/commit/e27032e8563fc4525904c9f09b8c68953a8340b1)).


## [0.18.0.3](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.3) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.2...0.18.0.3)) - 2018-07-27

### Misc
- Add the cli to the distribution package ([b403289](https://github.com/aeternity/aepp-sdk-python/commit/b40328970be54c38b700e933f9bbc4fae1010a61)).
- fix transitive dependencies installation for pip (#31) ([95b5b4b](https://github.com/aeternity/aepp-sdk-python/commit/95b5b4b839ee97f1cd297adc7ac49860aa7b8366)).


## [0.18.0.2](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.2) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.18.0.1...0.18.0.2)) - 2018-07-27

### Misc
- Feature/pypi package (#28) ([e663baf](https://github.com/aeternity/aepp-sdk-python/commit/e663baf3e2320b918e64905a384543f49b1f3ebb)).
- Merge branch 'master' into develop ([ee06cb9](https://github.com/aeternity/aepp-sdk-python/commit/ee06cb9a3ea744368280606af7f1c5c57d9095a7)).
- Release/0.18.0.2 (#30) ([c8420aa](https://github.com/aeternity/aepp-sdk-python/commit/c8420aa949c9528aec3bc618c1fe54ebbcf49382)).


## [0.18.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.18.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/0.15.0.1...0.18.0.1)) - 2018-07-27

### Misc
- Feature/epoch 0.18.0 (#26) ([9762f91](https://github.com/aeternity/aepp-sdk-python/commit/9762f91109c1b1130f6fc1d206d4bd3c790e96b5)).
- fix readme ([d6bce49](https://github.com/aeternity/aepp-sdk-python/commit/d6bce4950b96014b8ebd02f694c214b893e03bbe)).
- Merge pull request #25 from aeternity/bugfix/histories ([bbe5d38](https://github.com/aeternity/aepp-sdk-python/commit/bbe5d38be83c64304de848195e2bc26a5ed3b92a)).
- Release/0.18.0.1 (#27) ([ec75954](https://github.com/aeternity/aepp-sdk-python/commit/ec75954ee90c9756379d56f71544f15f5b5e45e7)).
- Update README.md ([0cad501](https://github.com/aeternity/aepp-sdk-python/commit/0cad5019a232994477b251c137666c853dd51664)).
- Update README.md ([7bb5e4c](https://github.com/aeternity/aepp-sdk-python/commit/7bb5e4c8ac27750fef771a1237044aab1d1f3995)).


## [0.15.0.1](https://github.com/aeternity/aepp-sdk-python/releases/tag/0.15.0.1) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/v0.13.0-0.1.0...0.15.0.1)) - 2018-07-10

### Misc
- Feature/contracts and 0.15.0 compatibility (#21) ([338682f](https://github.com/aeternity/aepp-sdk-python/commit/338682fac625070cce3891043b6c64a22e9d3a7a)).
- Feature/epoch 0.14.0 (#20) ([99de4e2](https://github.com/aeternity/aepp-sdk-python/commit/99de4e2fd669bfda49faeaf80ddd4917c6c785a6)).
- Feature/newcli (#22) ([c4fc340](https://github.com/aeternity/aepp-sdk-python/commit/c4fc34070449badd275e1b49f41b729a13a680ce)).
- Release/0.15.0.1 (#23) ([e798b0b](https://github.com/aeternity/aepp-sdk-python/commit/e798b0bcc001dbf12847ef7603e2e8f7998dbb3a)).


## [v0.13.0-0.1.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/v0.13.0-0.1.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/release/v0.8.0...v0.13.0-0.1.0)) - 2018-05-30

### Misc
- + Add basic configuration for jenkins ci ([5dad431](https://github.com/aeternity/aepp-sdk-python/commit/5dad43106431626a2cc9c9712339a14bdc64f52b)). Related issues/PRs: #14
- Add changelog ([ada0fd5](https://github.com/aeternity/aepp-sdk-python/commit/ada0fd59bec44e3cb690cb3f80d48f60381699f1)).
- added tests for CLI tool; encrypt the generated wallet with a password ([957781a](https://github.com/aeternity/aepp-sdk-python/commit/957781a46241df741c5e651416faf2613c3a8957)).
- CLI: improved password handling (optional --password parameter), more tests ([d1b2843](https://github.com/aeternity/aepp-sdk-python/commit/d1b28438ed08fb0c967600081911a40da44165dc)).
- Feature/openapi for epoch v0.13.0 (#17) ([667d4c3](https://github.com/aeternity/aepp-sdk-python/commit/667d4c30aa485ac2f0fdac8ab6f96a699a46daf4)).
- Feature/rlp  for epoch v0.10 (#16) ([30d3ded](https://github.com/aeternity/aepp-sdk-python/commit/30d3ded36e217c2600c1814e197465d2f98a9e19)).
- fixed calling the aecli spend function (used wrong signature for spend ([4bc5efb](https://github.com/aeternity/aepp-sdk-python/commit/4bc5efb4fdbcfad77434373795058615277eb141)).
- Merge pull request #15 from aeternity/feature/jenkins-ci ([98a79d8](https://github.com/aeternity/aepp-sdk-python/commit/98a79d846869e570ef3476a051f1c558836c4f78)).
- Release/0.13.0 0.1.0 (#19) ([b9a141a](https://github.com/aeternity/aepp-sdk-python/commit/b9a141a2d05b2d36b22fc6184e9b42bb411ef0ce)).
- Update README.md ([cb4f834](https://github.com/aeternity/aepp-sdk-python/commit/cb4f8347b41fdd15342f1aaa1f2dbd0f6c6dac32)).


## [release/v0.8.0](https://github.com/aeternity/aepp-sdk-python/releases/tag/release/v0.8.0) ([compare](https://github.com/aeternity/aepp-sdk-python/compare/55ed2bb49f742ad9dd932097a8b7796fa1458a64...release/v0.8.0)) - 2018-03-19

### Misc
- Add Docker support mode ([2f2e457](https://github.com/aeternity/aepp-sdk-python/commit/2f2e457474e5bb8183cbf798d0d7544e5945f3c0)).
- Add Fedora as supported OS using Docker ([733e9ad](https://github.com/aeternity/aepp-sdk-python/commit/733e9add7a6c1eeeb2a5540b36cddef8d93ef6f3)).
- Add instructions on how to install using venv ([2012311](https://github.com/aeternity/aepp-sdk-python/commit/20123110b7522edc81755709fc76e9e44af45a09)).
- added "aecli" executable that is a shortcut for `python -m aeternity` ([a2ee670](https://github.com/aeternity/aepp-sdk-python/commit/a2ee67038bdb57094667b5fa35f6bfe727b54398)).
- added assertion to enforce correct hash in `get_transaction_by_transaction_hash` ([0bad8cc](https://github.com/aeternity/aepp-sdk-python/commit/0bad8cc1b96f6092695a29b5e4c39f1d09294785)).
- added DTO for aens_transfer_tx ([ec61fce](https://github.com/aeternity/aepp-sdk-python/commit/ec61fcef9db0d844cc9e19b9635368b1ad41b084)).
- added formatter methods to print the Transactions and blocks nicely ([7cf4f2e](https://github.com/aeternity/aepp-sdk-python/commit/7cf4f2e050048cdc7c9d92d001c564b888e7f4b2)).
- added function to cli: `aecli wallet info <wallet path>`  to get the address of your wallet ([a782032](https://github.com/aeternity/aepp-sdk-python/commit/a782032df734bd2e5059b270e8ad1967f10d2827)).
- added more tests for the case of an invalid contract ([784590d](https://github.com/aeternity/aepp-sdk-python/commit/784590dc9022df4c098979d024611b9d7995b656)).
- added more transaction Types, fixed tests ([4e3fde9](https://github.com/aeternity/aepp-sdk-python/commit/4e3fde96d3064bce403c6fae885e77e77b1c2438)).
- added msgpack to requirements.txt ([e9b603b](https://github.com/aeternity/aepp-sdk-python/commit/e9b603bd464ef2da75a9f124fc22174b2a3f3379)).
- added top-level requirements.txt ([322c316](https://github.com/aeternity/aepp-sdk-python/commit/322c3169d55d633d4f002bbb77b1195b378cd696)).
- aecli: renamed `aens` command to `name` ([6766ff1](https://github.com/aeternity/aepp-sdk-python/commit/6766ff16ea12c3963bcbabf802dd19988b77a4a1)).
- After feedback from Tom ([ba28216](https://github.com/aeternity/aepp-sdk-python/commit/ba28216769c7bcec3f459d90470b06016e2257e7)).
- allow inspecting single blocks and transactions using the aecli tool ([ee21bd2](https://github.com/aeternity/aepp-sdk-python/commit/ee21bd2a3978a3bf4120a1ab271d29aff7b01241)).
- allow specifying salt when calling preclaim ([421358a](https://github.com/aeternity/aepp-sdk-python/commit/421358a7e50d26253ba15c4db86eaad3948a2ae9)).
- allow using multiple connections ([c613af3](https://github.com/aeternity/aepp-sdk-python/commit/c613af317342624b9789c6372d9dac12adb448e0)).
- always json encode the oracle response, cleanup ([8b295d0](https://github.com/aeternity/aepp-sdk-python/commit/8b295d02c45a8204f991ab6d2d8655339f68f23a)).
- changed --no-input to --force switch, halfway implemented oracle CLI interface, refactoring ([8ceb646](https://github.com/aeternity/aepp-sdk-python/commit/8ceb6462fc839d20ac6c1d10c56fb88cf1eb3685)).
- changed CLI parameter `--no-input` to `--force` ([ab9cf14](https://github.com/aeternity/aepp-sdk-python/commit/ab9cf1481436763a1e2f0e0cb14f8c35315e507a)).
- Changed Config object: Allow setting host and port individually ([e36dd0d](https://github.com/aeternity/aepp-sdk-python/commit/e36dd0d7c76dc82988b78875a7bb07480064abeb)).
- changed signature of `client.spend` so that it has the keypair as first argument like all other calls ([6007ae6](https://github.com/aeternity/aepp-sdk-python/commit/6007ae68a035bf589414ea932e92a0cf8f4dc79d)).
- clean up of tests ([9bd0a2d](https://github.com/aeternity/aepp-sdk-python/commit/9bd0a2d6d53e8707800093d5966f90013f598da6)).
- cleanup, removed custom Exception (i think it's overengineered) ([f7da781](https://github.com/aeternity/aepp-sdk-python/commit/f7da7819f17d875282d37f8a079be5a03f08a161)).
- Debug which URL is going to be queried ([dfc6281](https://github.com/aeternity/aepp-sdk-python/commit/dfc62817aeaae7c82ea15dec39f5941e937c5642)).
- do not automatically register to the new_block event when initializing the EpochClient ([1d8bb80](https://github.com/aeternity/aepp-sdk-python/commit/1d8bb803e58a84d12c8f39cba581af856741c593)).
- Fix amount ([d1eb718](https://github.com/aeternity/aepp-sdk-python/commit/d1eb718428c5fa50069411f5ff7af4ab4b1484fd)).
- fixed AENS tests, some fixes to keep the interface of AEName stable ([4e926c3](https://github.com/aeternity/aepp-sdk-python/commit/4e926c34f596fe59cc49255c996c65dfab7894c4)).
- fixed all tests in test_api ([95e78a5](https://github.com/aeternity/aepp-sdk-python/commit/95e78a5030aeb7b8e8daa9d05c3aff55bbc1f63f)).
- fixed contract tests using aer-contract language ([accc104](https://github.com/aeternity/aepp-sdk-python/commit/accc1041036be932793eed714094f7e798a374b4)).
- Fixed merge-conflicts, using new EpochClient http interface for spend Merge branch 'master' into develop ([a75510f](https://github.com/aeternity/aepp-sdk-python/commit/a75510ff1d08257b736ece18aea436199c093397)).
- fixed test_api.py when chain contains AENS transactions ([e63a7d3](https://github.com/aeternity/aepp-sdk-python/commit/e63a7d3417fedfebdf3a9a9ff7d7066c08c3b255)).
- got examples to work, is able to call an API by url and return some json ([8395c35](https://github.com/aeternity/aepp-sdk-python/commit/8395c3550fe4217bdc5e94c827a677c89f5e7271)).
- got first implementation of the oracle wrapper to work (including full lifecycle test) ([b9620d7](https://github.com/aeternity/aepp-sdk-python/commit/b9620d76752bacddf45aca8559ee7345685e4551)).
- got offline transaction signing to work ([e5aa572](https://github.com/aeternity/aepp-sdk-python/commit/e5aa572164943f7f7c02ac6864625b64ca06380c)).
- got offline transaction signing to work ([cd0b331](https://github.com/aeternity/aepp-sdk-python/commit/cd0b3310ef47f27312b5ae13dc9cdf8e7ec16a04)).
- Ignore local epoch clone ([cb89584](https://github.com/aeternity/aepp-sdk-python/commit/cb89584aac68b19b512ac86c0f66e12a62a72980)).
- implemented AENS name transfer using offline signed transactions ([86ff7b5](https://github.com/aeternity/aepp-sdk-python/commit/86ff7b599cf144c66cdca54f39b000f5080ef211)).
- implemented all API functions provided by the swagger interface ([7ba4835](https://github.com/aeternity/aepp-sdk-python/commit/7ba4835451a237dd83890662259a6737ff619977)).
- implemented base58 ([f178c85](https://github.com/aeternity/aepp-sdk-python/commit/f178c8523e20f8bb442a1d77f543547ae233b203)).
- Implemented changes as discussed in https://github.com/aeternity/dev-tools/pull/2 ([81dab0a](https://github.com/aeternity/aepp-sdk-python/commit/81dab0a534de54f81d52a3ff8f5e0fb0445ce6e7)).
- implemented CLI for creating wallets ([6ccf3a4](https://github.com/aeternity/aepp-sdk-python/commit/6ccf3a479f79ff7b09b1de642e26df7fa5a474eb)).
- implemented CLI interface for `balance` and `height` ([586a6e3](https://github.com/aeternity/aepp-sdk-python/commit/586a6e3fbd06ed72585df6c158e58387c1fa32a8)).
- implemented CLI oracle query ([ed8c0a8](https://github.com/aeternity/aepp-sdk-python/commit/ed8c0a80942ca30c0491922f7fc8dab5b42f535c)).
- implemented offline signing of AENS update transactions ([bfeacae](https://github.com/aeternity/aepp-sdk-python/commit/bfeacaec0d52aa4d30e822f71d0f629905ecfe2d)).
- implemented the interface to call contract functions ([e7fc623](https://github.com/aeternity/aepp-sdk-python/commit/e7fc623dfa7a0bb60a8fb40e993fa2341967431e)).
- improved CLI, updated spend functionality to use offline signing instead of internal endpoint ([4091e54](https://github.com/aeternity/aepp-sdk-python/commit/4091e54a7b5ba6ed375e5cbb93a0ae81662ba0c3)).
- improved transaction test: make sure that the signed transaction appears in the chain ([ebb4585](https://github.com/aeternity/aepp-sdk-python/commit/ebb45852cbf28fb7f4810f77c69e2e22b30550c5)).
- made changes as requested in review https://github.com/aeternity/aepp-sdk-python/pull/7 ([393d0a7](https://github.com/aeternity/aepp-sdk-python/commit/393d0a7cb5c587a28d1862367bd69ff6696b87f4)).
- made cli `balance` command better for piping into other programs ([b6633ce](https://github.com/aeternity/aepp-sdk-python/commit/b6633ce19896c9443abd41e6f73a8b1aca72afa2)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([cc468ae](https://github.com/aeternity/aepp-sdk-python/commit/cc468ae3d1d6fe807a6bef16095443ae69ddc031)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([bb1582a](https://github.com/aeternity/aepp-sdk-python/commit/bb1582aac0e8ab46f57beb4331172d921096e069)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([6c6ef1c](https://github.com/aeternity/aepp-sdk-python/commit/6c6ef1c1929efac7f790ba326c4a4c6cf3ae274a)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([deeb3ea](https://github.com/aeternity/aepp-sdk-python/commit/deeb3ea6a88c02cd3c21b16873905c7d58935686)).
- Merge branch 'develop' of github.com:aeternity/aepp-sdk-python into develop ([afaf013](https://github.com/aeternity/aepp-sdk-python/commit/afaf013a9ea8b55a4f8c53fb7aa3d2b093ba32c4)).
- Merge branch 'master' into develop ([f953888](https://github.com/aeternity/aepp-sdk-python/commit/f953888ba3333cf85809315ac8afa696fb9f7f6a)).
- Merge branch 'master' into master ([be36c37](https://github.com/aeternity/aepp-sdk-python/commit/be36c376e94b8081e455eae68f9890ed4b2dd346)).
- Merge branch 'master' into release/v0.8.0 ([a643a56](https://github.com/aeternity/aepp-sdk-python/commit/a643a56abc6aa38008f0e543db65e447630b0248)).
- Merge pull request #10 from andi-apeunit/master ([eb396af](https://github.com/aeternity/aepp-sdk-python/commit/eb396af55d5bcb10309c30e93734f20d3c6fa69b)).
- Merge pull request #11 from aeternity/develop ([4330c08](https://github.com/aeternity/aepp-sdk-python/commit/4330c08ba4ca1a889c90db2afb5aac6030ba9852)).
- Merge pull request #12 from aeternity/jsnewby-patch-1 ([2bb7963](https://github.com/aeternity/aepp-sdk-python/commit/2bb796399d5a267846e2ce8e86dd278fc12db8fd)).
- Merge pull request #2 from aeternity/develop ([947c259](https://github.com/aeternity/aepp-sdk-python/commit/947c2596cf7efbed4238d7adbf740c11486103a1)).
- Merge pull request #4 from aeternity/develop ([1c748c8](https://github.com/aeternity/aepp-sdk-python/commit/1c748c8a4b23e0ed2d239b6e7ec673f18ccc9cc0)).
- Merge pull request #5 from aeternity/tillkolter-patch-1 ([ebc47cf](https://github.com/aeternity/aepp-sdk-python/commit/ebc47cfdebaa87fbb1b9e79e539b12ec5ce133c1)).
- Merge pull request #6 from aeternity/newby-spend-tx ([10835c0](https://github.com/aeternity/aepp-sdk-python/commit/10835c07b88ff7ea4d2e839031e9adb0ee184aac)).
- Merge pull request #7 from aeternity/develop ([0aefa39](https://github.com/aeternity/aepp-sdk-python/commit/0aefa39f1c3db65cbf1278bf5bf63edf27ff4d12)).
- Merge pull request #8 from aeternity/develop ([d577011](https://github.com/aeternity/aepp-sdk-python/commit/d577011286366e9ad8d60d94ff8776607995f35c)).
- Merge pull request #9 from aeternity/feature/config-refactor ([db28788](https://github.com/aeternity/aepp-sdk-python/commit/db287882cd83e0b9d5f5e48f371c25e8c80d1848)).
- Moved the project from aeternity/dev-tools to aeternity/aepp-sdk-python ([55ed2bb](https://github.com/aeternity/aepp-sdk-python/commit/55ed2bb49f742ad9dd932097a8b7796fa1458a64)).
- print help when no arguments are given ([9da4b2b](https://github.com/aeternity/aepp-sdk-python/commit/9da4b2b826ae4cab3144e252b08f588ed409ed05)).
- Properly configure the root logger ([01da450](https://github.com/aeternity/aepp-sdk-python/commit/01da4508d2780e201ea0b1157a809d86f51660a1)).
- README: updated cli usage ([6de55be](https://github.com/aeternity/aepp-sdk-python/commit/6de55bedc315d9154f5e9ffdb6db4322c55b2d9f)).
- Refactored Oracle to use a single state, moved initialization to constructor ([35932ad](https://github.com/aeternity/aepp-sdk-python/commit/35932ada99dc2173579ef08e82bc11f4855af615)).
- refactored OracleQuery to use constructor instead of class attrs, documentation ([1224ad5](https://github.com/aeternity/aepp-sdk-python/commit/1224ad55b68ad2165499b5f4832432a529c45555)).
- refactoring and made tests for AENS and contracts run through ([eb707df](https://github.com/aeternity/aepp-sdk-python/commit/eb707df87adbe098b62b23ff4a49dc6ac79ad059)).
- removed broken import ([fe289d5](https://github.com/aeternity/aepp-sdk-python/commit/fe289d5f54c58738b7f45c11ceac8a285a7eee82)).
- removed unused code ([26c76d1](https://github.com/aeternity/aepp-sdk-python/commit/26c76d1263b76088360d865f30c6ccbd20453036)).
- removed whitespace at line endings ([b74661e](https://github.com/aeternity/aepp-sdk-python/commit/b74661e8578bbb4584664742ee30f07f2befc791)).
- renamed `client.local_*` calls to `client.external_*`, use offline signing for AENS preclaim and claim ([e81328d](https://github.com/aeternity/aepp-sdk-python/commit/e81328d903e9b1ca412fe6763fb7c0b0b72c7f4c)).
- renamed `create_transaction` to `create_spend_transaction` ([ba35fa4](https://github.com/aeternity/aepp-sdk-python/commit/ba35fa4e040355c27fe94d78bfde64ec37929879)).
- renamed `get_current_height` to `get_height`, let `Contract` object contain the code ([3d4770b](https://github.com/aeternity/aepp-sdk-python/commit/3d4770bbcc03ec4aa77495b3b6c0aedc01288951)).
- renamed `get_current_height` to `get_height`, let `Contract` object contain the code ([0c5d659](https://github.com/aeternity/aepp-sdk-python/commit/0c5d65980e896e4ede27ac59bc5fecf415cea9e3)).
- renamed EpochClient.run to EpochClient.listen ([9d2b2c4](https://github.com/aeternity/aepp-sdk-python/commit/9d2b2c48c3be552cea45b8656c9d76eaeb477ef3)).
- Return tx_hash ([15df14e](https://github.com/aeternity/aepp-sdk-python/commit/15df14ee7f4a09853546ef0490b7afd71de31a88)).
- Return tx_hash not tx ([c733609](https://github.com/aeternity/aepp-sdk-python/commit/c73360960de1dfe61a0ab763c60e4d6c660be929)).
- Return tx_hash on spend transaction ([55ba0c1](https://github.com/aeternity/aepp-sdk-python/commit/55ba0c1a15c5d1f1037317c75150e218965d750d)).
- run tests for both EVM and RING ([76ae1ee](https://github.com/aeternity/aepp-sdk-python/commit/76ae1ee7fc35608a5ff90a82a45aee6cc8d1b52c)).
- Set tx_hash on signable transaction ([1d22ec9](https://github.com/aeternity/aepp-sdk-python/commit/1d22ec9de9b363c99bc5933b5d48326a02ef3506)).
- show error when using invalid oracle command ([699e52e](https://github.com/aeternity/aepp-sdk-python/commit/699e52efc5f6d9b8cdfb24e40e0b71d6fe6b1557)).
- skipping failing tests for now: those need to be fixed when offline signing the AENS transactions ([e6418bc](https://github.com/aeternity/aepp-sdk-python/commit/e6418bc189bc190c3eeb16731674e7af890eccb1)).
- some test cleanup ([9fc2d5f](https://github.com/aeternity/aepp-sdk-python/commit/9fc2d5fb834b705742e11d0d9da37c6c854cfa3a)).
- Spend function and example ([642a682](https://github.com/aeternity/aepp-sdk-python/commit/642a682a616c19155c1071711b6d810aacc45ae7)).
- trailing comma ([9c1725d](https://github.com/aeternity/aepp-sdk-python/commit/9c1725d273480c0c3a35305f1a1cca99d00c59d0)).
- transaction signing WIP ([14111b7](https://github.com/aeternity/aepp-sdk-python/commit/14111b730dbca48726a207fc56373f548f2faaec)).
- transaction signing WIP (almost there...) ([a40eda7](https://github.com/aeternity/aepp-sdk-python/commit/a40eda74fff6856a311708e13681605b80d18beb)).
- transaction signing WIP (almost there...) ([19c42ab](https://github.com/aeternity/aepp-sdk-python/commit/19c42abafec187b3c6d0b134b615766d15f27768)).
- update ([92124f6](https://github.com/aeternity/aepp-sdk-python/commit/92124f616609c6e57120fca3a94aa58e29cc66f0)).
- update ([9fbfa28](https://github.com/aeternity/aepp-sdk-python/commit/9fbfa2880afc92f10f442f9424bec28b507aa8f1)).
- Update epoch.py ([cebc245](https://github.com/aeternity/aepp-sdk-python/commit/cebc2456c297627616733b2f771e6d356c04e439)).
- Update INSTALL.md ([7a596c5](https://github.com/aeternity/aepp-sdk-python/commit/7a596c5a9ec223877d64afff6170b368ea8d6b09)).
- Update README.md ([065ec64](https://github.com/aeternity/aepp-sdk-python/commit/065ec647beb83d5bd294eb34fdf74943541f0e81)).
- Update README.md ([d463778](https://github.com/aeternity/aepp-sdk-python/commit/d4637787cbd5ae1ec98887aab964b56f1154c200)).
- Update README.md ([a9062e3](https://github.com/aeternity/aepp-sdk-python/commit/a9062e3cf2d331896a9bcea73d2c4dece3c6a16d)).
- Update README.md ([7cf09a2](https://github.com/aeternity/aepp-sdk-python/commit/7cf09a277476e12d0d82a87006ada0e87ae6a423)).
- Update README.md ([3c395bc](https://github.com/aeternity/aepp-sdk-python/commit/3c395bc243c757afa7c2fc7795ebf622e1b8bf88)).
- Update README.md ([ace41ae](https://github.com/aeternity/aepp-sdk-python/commit/ace41ae21b7dd25efd901bbe02ae30042c005867)).
- Update README.md ([58815a4](https://github.com/aeternity/aepp-sdk-python/commit/58815a498e919fa132e0c4583fcad10d6384f9f0)).
- Update README.md ([d8a971f](https://github.com/aeternity/aepp-sdk-python/commit/d8a971f70f92002b0954411c98d09e77bc403640)).
- updated contract interface to be compatible with the latest master using switchable ABI ([a48e49b](https://github.com/aeternity/aepp-sdk-python/commit/a48e49b47903299c62b6875d694e541cb32ab840)).
- updated Readme containing the planned spec for the API (oracle parts are only partly implemented) ([3c6c5c8](https://github.com/aeternity/aepp-sdk-python/commit/3c6c5c84310dd9cac55933699b7979c5d3cbc6eb)).
- updated test_api.py to expect the epoch to be in version 0.8.0 ([c0975d4](https://github.com/aeternity/aepp-sdk-python/commit/c0975d47116c82c2af639b5d7dd46031763c3fff)).
- updated the README for aecli tool ([2ea6053](https://github.com/aeternity/aepp-sdk-python/commit/2ea605321a219958e4a5badffc85b881566249f1)).
- use AENSException instead if InvalidName Exception ([7ebb9f4](https://github.com/aeternity/aepp-sdk-python/commit/7ebb9f4af34a4b2fc2e7260ec2443a47b78d79c5)).
- Use single quotes, not double ([288562d](https://github.com/aeternity/aepp-sdk-python/commit/288562dea9ad45f720c0eb620c98425e5448b02d)).
- use transaction signing for name revocation ([4e86ecf](https://github.com/aeternity/aepp-sdk-python/commit/4e86ecff0bf79f5dedc54eef8a7223049a50ea51)).
- whoopsie ([c55fbe5](https://github.com/aeternity/aepp-sdk-python/commit/c55fbe5e5dcbe4244a0748eb1eb2b0e2f11ada6b)).


