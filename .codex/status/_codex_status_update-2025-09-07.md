# Codex Audit (2025-09-07T10:43:32Z)

## Prompt
- File: `/workspace/_codex_/AUDIT_PROMPT.md`
- SHA-256: `24dcedbd430f9fdcd8aea7e866bd60a340c24bba1856400f057caef79ca1781b`

## README
- File: `README.md`
- SHA-256: `e67a1e5bcc8aa1284276d98acaf2f065beb5d066c36e602dd61871761e3a34b0`
```
# codex-universal

`codex-universal` is a reference implementation of the base Docker image available in OpenAI Codex.

This repository is intended to help developers customize environments in Codex by providing a similar image that can be pulled and run locally. This is not an identical environment but should help for debugging and development.

> **Policy:** No GitHub-hosted Actions. Run `make codex-gates` locally or on a self-hosted runner (ephemeral runners recommended).

For more details on environment setup, see OpenAI Codex.

For environment variables, logging roles, testing expectations, and tool usage, see [docs/guides/AGENTS.md](docs/guides/AGENTS.md).

## Local CI (no GitHub-hosted Actions)

Run the gates locally or on a self-hosted runner.

```bash
# Standard path (coverage gate enforced at 70%)
nox -s tests
```

# Fast paths vs isolation
We support fast developer loops while keeping a hermetic fallback:

**Fast paths**
- `nox -r` — reuse venvs between runs (no reinstall). :contentReference[oaicite:7]{index=7}
- `nox --no-venv` — run sessions in the current interpreter (no venv creation). Great for quick checks. :contentReference[oaicite:8]{index=8}
- `uv` inside sessions — ultra-fast installs (`uv pip install ...`). If `uv` isn’t found, we fall back to `pip`. :contentReference[oaicite:9]{index=9}

**Hermetic fallback**
- Build an offline **wheelhouse** once, then install from it with `--no-index --find-links`. See `tools/make_wheelhouse.sh` and `tools/bootstrap_wheelhouse.sh`. :contentReference[oaicite:10]{index=10}

**Trade-offs**
- Fastest: `nox --no-venv` + `uv` (uses your current env; not isolated). :contentReference[oaicite:11]{index=11}
- Balanced: `nox -r` (reused venvs, isolated enough, still quick). :contentReference[oaicite:12]{index=12}
- Most isolated/offline: install from wheelhouse (`pip install --no-index --find-links`), consistent and network-independent. :contentReference[oaicite:13]{index=13}

> Note: We intentionally keep **coverage fail-under at 70%** until
```

## Inventory
- Files: 730

<details><summary>Show inventory</summary>

```json
[
  {
    "path": "_codex_status_update-2025-09-03.md",
    "size": 10015,
    "sha256": "943b73221c3ea95d5c3b6063d493c7d6a846a4ee5bab9d5fb730bc6e819e1ff5"
  },
  {
    "path": "codex_script.py",
    "size": 21502,
    "sha256": "31b2ad83665a581ad78fb720922f4c022ee9827030be4e1c9a6bf2951526f0cf"
  },
  {
    "path": "DEFERRED.md",
    "size": 80,
    "sha256": "fed2341fde1ce3765c45949c61550243eaa312c7b85b6221b0bea5151add91ec"
  },
  {
    "path": "_codex_status_update-2025-09-04.md",
    "size": 10166,
    "sha256": "e1de3ff126deb3eb9fc4709e32c6e4fa0e9f05562cb830fac583ef88451fe1e9"
  },
  {
    "path": "README.md",
    "size": 30881,
    "sha256": "e67a1e5bcc8aa1284276d98acaf2f065beb5d066c36e602dd61871761e3a34b0"
  },
  {
    "path": "codex_local_gates.sh",
    "size": 334,
    "sha256": "0f3c9af806b55bd729ccffca4302c498683bf79a8abd70b15f8f7eae96190240"
  },
  {
    "path": "_codex_status_update-2025-09-07.md",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "docs/changelog/CHANGELOG_Codex.md",
    "size": 6123,
    "sha256": "018ad9c2adff3b2b95c3c87a6fa717014ddb27464e070de2729764d805cc271d"
  },
  {
    "path": "CONTRIBUTING.md",
    "size": 2386,
    "sha256": "a7db48197c6f7d3ebd918ebe8b534184710ef231073a9729f56c99b3a5aacad4"
  },
  {
    "path": ".coveragerc",
    "size": 119,
    "sha256": "456966507401a569fb83e5490436af7664af87255152454d2f4d9f70873713b5"
  },
  {
    "path": "Codex_Questions.md",
    "size": 8055,
    "sha256": "fcd1aa7570a559d8046a20f3580467ef152e37fa18b934321c6cac54aba26ea3"
  },
  {
    "path": ".gitattributes",
    "size": 730,
    "sha256": "2cdc43489e495f5c4ace50d19c91d16e47dee5362492316c8b0e395504ac8d67"
  },
  {
    "path": "codex_setup.py",
    "size": 8607,
    "sha256": "cd442ad93b47aa8bc87ca42be3b203535ce69043936fa866f0bf5f49c8189911"
  },
  {
    "path": ".gitignore",
    "size": 371,
    "sha256": "51925a7485b41cd9eafb606da8a67b4821e1b5455893986ba34b5e1d84c09c56"
  },
  {
    "path": "ci_local.sh",
    "size": 240,
    "sha256": "65490eaa08d1a5f1d7d1691ce997560f4d3cb906fbea1c4109b3baed7277f866"
  },
  {
    "path": "codex_migration.zip",
    "size": 4208,
    "sha256": "e81dc1163e60a276aac4ffee599db849ec06cea95ba0e8e7e4d2918bd784d0fe"
  },
  {
    "path": "requirements.txt",
    "size": 151,
    "sha256": "ad97ed471c8949751fce2db3cbb8b5bd99370ecfc0f3790977aa544f41253383"
  },
  {
    "path": ".pre-commit-config.yaml",
    "size": 1982,
    "sha256": "7bfe0b316fcd0a73a95714e18d21a0d575ba2e3b8884c20de659d7cd6282eecc"
  },
  {
    "path": "PINNED_SHAS.md",
    "size": 1161,
    "sha256": "1cf0f0b9d88f47975bafa18aef033d3d650d48a0d866015b9d6adee19d8c9487"
  },
  {
    "path": "_codex_status_update-2025-08-31.md",
    "size": 528,
    "sha256": "3e2513e3d7e436242152f549bbcbf57312f92ade7210bd28b8b2208111009ced"
  },
  {
    "path": "_codex_status_update-2025-08-28.md",
    "size": 20206,
    "sha256": "24bf451a264891862771dd1916f85c41684eebd6858a33b01facc6465b73635d"
  },
  {
    "path": "ERROR_CAPTURE_BLOCKS.md",
    "size": 3144,
    "sha256": "95bd3a044a4aec6813a25161b9346ee43451dafd075927f444f491c90177af45"
  },
  {
    "path": "bandit.yaml",
    "size": 10,
    "sha256": "c08f48b72f819be9b678d23a2432ca2dd87a6ad070888d4acce68e61e9660946"
  },
  {
    "path": "deploy_codex_pipeline.py",
    "size": 3382,
    "sha256": "ea7254591a23e5735ab23cb5e820d0cf800c42b712233179048c991f1ac7aa82"
  },
  {
    "path": "fallback_patch_4.1-4.8.diff",
    "size": 6991,
    "sha256": "beae94826682df9dfef2f9b2043b3d5cb4714e365a543fae41043e29a3d8092f"
  },
  {
    "path": "analysis_metrics.jsonl",
    "size": 824,
    "sha256": "d962979cd2f5d5a8f1bdcae5765ddc0cf549cc2f34f4f0120ce275b85a6240eb"
  },
  {
    "path": "RESEARCH_QUESTIONS.md",
    "size": 1104,
    "sha256": "e7d5fe853aca728198408168cad296fb7de574c9ddada590e155e5d654c9bf05"
  },
  {
    "path": "docker-compose.yml",
    "size": 996,
    "sha256": "e3335c0511ec59ce24f864cb6a6acd998c2c007e3d105d0535c1714bc51df805"
  },
  {
    "path": "CODEBASE_AUDIT.md",
    "size": 10880,
    "sha256": "107c8ccc3cbf3563563c477f741d0abd875dd9df4d8cf399bc8e84c3467bff85"
  },
  {
    "path": "_codex_status_update-2025-09-02.md",
    "size": 7668,
    "sha256": "793cd1e5b5e3727a66e1598ad2b919e99551e0891f59f4b50f732a8a12c3eada"
  },
  {
    "path": "docs/ops/RUNBOOK.md",
    "size": 7363,
    "sha256": "98e95c1bcfdee3f82ba7a2f3ab98cf0c7622487b8ec3ed4c62dd6b54516b3fbe"
  },
  {
    "path": "codex_run.log",
    "size": 73,
    "sha256": "c592b417b1631d82e32947552e655642a28bfb9137717da22c378a79242c07a0"
  },
  {
    "path": "requirements-dev.txt",
    "size": 188,
    "sha256": "674d35837b81dc71e05bd13418e275f5ad091b25b62c13823abc27136f64d2bf"
  },
  {
    "path": "docs/guides/AGENTS.md",
    "size": 10350,
    "sha256": "dda825d9a7d93e46e67cf6ae5dd8245e56ff0117589915f97afac54231f391f4"
  },
  {
    "path": "MERGE_NOTES.md",
    "size": 1472,
    "sha256": "ea4380fcbee4f399604b8ae1b45fd5b4480dcf6a89fe879c8bca2aa35c272f2d"
  },
  {
    "path": "AUDIT_PROMPT.md",
    "size": 4166,
    "sha256": "24dcedbd430f9fdcd8aea7e866bd60a340c24bba1856400f057caef79ca1781b"
  },
  {
    "path": "pytest.ini",
    "size": 538,
    "sha256": "5d0b37257356c5896b5026132160818777bd8f2624d63374fe888dbb870ea6af"
  },
  {
    "path": "requirements.lock",
    "size": 2626,
    "sha256": "59de5d70e8b949ef6b8375edd535163af1fe7b0932a42bb4802f9dce33886d4a"
  },
  {
    "path": "_codex_status_update-2025-08-29.md",
    "size": 477,
    "sha256": "6a15ddec14039780705fe3203967ffdbf132f89040525d657bbdca66f3ab6f33"
  },
  {
    "path": ".env",
    "size": 84,
    "sha256": "e73bbce4ed6f57875bf3ec20c340ec139a167929488c30d59623211d722dd21d"
  },
  {
    "path": "entrypoint.sh",
    "size": 622,
    "sha256": "639330725f6d62f4ac78373b93ec13bb1d2cd51418f1ceeabe9b70220726bb2f"
  },
  {
    "path": "codex.mk",
    "size": 4141,
    "sha256": "9b890d7f8fff48c9ae612aa44878697600f161324f81421be12051f0c693257e"
  },
  {
    "path": "codex_ast_upgrade.py",
    "size": 14551,
    "sha256": "53f79e2fc1e1cffbb43e5cf006bab23eab06fb3dc0468c32cd8184b127c2096b"
  },
  {
    "path": "docs/changelog/CHANGELOG_CODEX.md",
    "size": 1029,
    "sha256": "da457eddc1a9986dc48d33f73fdd20c9db20b6340a82c19f94bcdee58ea8198c"
  },
  {
    "path": "README_UPDATED.md",
    "size": 4767,
    "sha256": "4f8b31d851e20f04d8fe54afc44c0307e75af39c21bcd0aa9f8ba8faa4a0f0a8"
  },
  {
    "path": "setup.sh",
    "size": 15591,
    "sha256": "d0d8313cedc2bbb155407de6614cd4b588187652ba61f9dde615c8a1d538cb6e"
  },
  {
    "path": "_codex_status_update-2025-08-30.md",
    "size": 596,
    "sha256": "60022cf9ac3634bd0a58ce0d055642655254175f149e5a641efbf15ef30a3cb1"
  },
  {
    "path": "Dockerfile",
    "size": 916,
    "sha256": "647b1d4bf07600e3bdddb5138b2e88bcfd0668062cd7cbdd1c25b65f0d0c4df3"
  },
  {
    "path": "errors_codex.log",
    "size": 1406,
    "sha256": "857f7fabdec32889aa9f7fe0fc37084f71dd5bfd6ddb053825709bc53628117f"
  },
  {
    "path": ".pre-commit-hybrid.yaml",
    "size": 1169,
    "sha256": "ea250b9e2f79a27f81b4d9f9577ad0f7e147c859c2ef410dea06cf93b12f220d"
  },
  {
    "path": "setup_universal.sh",
    "size": 2434,
    "sha256": "a30ae512d15a8fdc3ce245fe29e5bc1cdaaf4d16107510d9e22a36615ab44050"
  },
  {
    "path": "CHANGELOG.md",
    "size": 1422,
    "sha256": "66f563a9b5b501a5a95653caf59b54c1cea4a59a0a70e14841c0fae74dcab499"
  },
  {
    "path": "tox.ini",
    "size": 542,
    "sha256": "c03361c370d6d52cb6563a4904d7869f874b9d7bd73af2f1863fdc6cd2c00c06"
  },
  {
    "path": "uv.lock",
    "size": 562009,
    "sha256": "4086f3871802b8da0bcec481ea34c2b49a37c7bb463f9e5e9394d4bac0da466d"
  },
  {
    "path": "CODEBASE_AUDIT_2025-08-26_203612.md",
    "size": 19863,
    "sha256": "a7f4680fbcdf37661aedf0c3ee7ade4617b96140d608a3362955492fcbd35de1"
  },
  {
    "path": "GATES_REPORT.txt",
    "size": 129,
    "sha256": "2bd1c1e7f59eaef7c980e87a53284cb462a4707385e2de353d011fa1af21e7da"
  },
  {
    "path": ".pre-commit-ruff.yaml",
    "size": 1148,
    "sha256": "5dcd904b3b40aff9d5af542ebfe6347b77c6866b3560ed9bd02fced022d3e468"
  },
  {
    "path": "Makefile",
    "size": 1482,
    "sha256": "6b9b6ba371f43d8d8f6c4b9a1710cbfcab0914d4622096b719612401c56648d0"
  },
  {
    "path": "pyproject.toml",
    "size": 2091,
    "sha256": "4bf5b073338840e87db2d08cb04af98b2979d9e417a86ecab6347729c61e9d72"
  },
  {
    "path": "docs/changelog/CHANGELOG_SESSION_LOGGING.md",
    "size": 372,
    "sha256": "038d23d6bb9aad6ade656ced5c9673567a914d7b223add0d6b14b968f7cf8e42"
  },
  {
    "path": "REPRO_NOTES.md",
    "size": 185,
    "sha256": "d4e1fa08cf0c9eea6b7cb88102991ba300481606a2d40de6eb6440c813137c1c"
  },
  {
    "path": ".secrets.baseline",
    "size": 5981,
    "sha256": "de7c7abcf8be1d4bfd2e2c06f1fdb699b06620e0a4da51687a044982bead333c"
  },
  {
    "path": "mkdocs.yml",
    "size": 732,
    "sha256": "ef1dc7044b9f9234d7e499389afe239fc1089d9260611743ae5908af1bfad276"
  },
  {
    "path": "codex_workflow.py",
    "size": 15258,
    "sha256": "2df5c0e29cf3a8c9e9557d68c92902a1e63c870b9ce2e480d163fa1953bef57b"
  },
  {
    "path": "noxfile.py",
    "size": 8298,
    "sha256": "0d7b4afc253b93d941054d645786914cd975ead6f855623ac160ef74ec44d55c"
  },
  {
    "path": "docs/changelog/CHANGELOG_codex.md",
    "size": 4647,
    "sha256": "e052215dabd9dae71802d1a17ab17bc8197685983d4edb09545806a73edeb28e"
  },
  {
    "path": "_codex_status_update-2025-09-05.md",
    "size": 15277,
    "sha256": "314c007c4a28133e617592923f2a5cced91183c94236b67cbfded30d82dedd5d"
  },
  {
    "path": "functional_training.py",
    "size": 28348,
    "sha256": "b93e5a7da90dcebdb9ec161fdf1d04abbb5f72f83a20d801594e60fd74aedc0d"
  },
  {
    "path": "configs/base.yaml",
    "size": 464,
    "sha256": "09b36c294293d6b99c07f8f34bb5a49b5289bda634018a3620e168819e2be0ad"
  },
  {
    "path": "configs/interfaces.example.yaml",
    "size": 292,
    "sha256": "5b2c73b6038188520d2762b9a0fd2860f1d4b1f31b1e88717e063551e419ebc8"
  },
  {
    "path": "configs/config.yaml",
    "size": 757,
    "sha256": "181736943808566d18e4dbc0691edd8a058b0aafb3bd8a8a255579a348db0ef8"
  },
  {
    "path": "configs/__init__.py",
    "size": 17,
    "sha256": "31b557cbc6c6bb4c8a7a1ce076067f99f5a5606bc875bd5d6362f2ef99dfb8f1"
  },
  {
    "path": "configs/train_tokenizer.yaml",
    "size": 148,
    "sha256": "5995ebe37e45a2d6fda57de147fd51ae3e2f173ea964eb8aeb6faa73192d0258"
  },
  {
    "path": "configs/tokenization/base.yaml",
    "size": 289,
    "sha256": "2aea91a42ab2f70c56666bdc2037489b59204f9117c530579d68c99951b46ab6"
  },
  {
    "path": "configs/env/ubuntu.yaml",
    "size": 145,
    "sha256": "c07246937c888a9ad3c7927f179add92cee4a2df74f95c03bc6bc9938231f7b2"
  },
  {
    "path": "configs/training/base.yaml",
    "size": 392,
    "sha256": "5d114dd212c1b4e895a499f25dfa566416acecfcde6dbf7119df36745eed66ca"
  },
  {
    "path": "configs/training/sweep_example.yaml",
    "size": 278,
    "sha256": "79d53f12373378349cf831d3242c779dc7fc606f51c8fa9c437d34259724ccec"
  },
  {
    "path": "codex_utils/logging_setup.py",
    "size": 1280,
    "sha256": "23c573d2b94cb28473c2cb335cf370bd61a1d4707966fafac025c33ee58fa91e"
  },
  {
    "path": "codex_utils/mlflow_offline.py",
    "size": 1033,
    "sha256": "91dcceec1cb70051d31ffd16476c87b2032841f269d12bbe771e19162cafd147"
  },
  {
    "path": "codex_utils/repro.py",
    "size": 3332,
    "sha256": "e2fdf84463ab355a5214f515fc7cc8d0cd44f537623fb4017cf084e81b00d12a"
  },
  {
    "path": "codex_utils/__init__.py",
    "size": 167,
    "sha256": "2347fa324d46cb7d81712d0dd3cb1d917d398bbf9245f7025e2c44d8fba8f8cb"
  },
  {
    "path": "codex_utils/ndjson.py",
    "size": 620,
    "sha256": "ca12674e81ae48f1c0f5410785293adcc33db97f9f773ea1b650b300d59fa0e0"
  },
  {
    "path": "deploy/helm/values.yaml",
    "size": 134,
    "sha256": "123827cc6d7e49df60cca2f2ca122c07482ed439408b91a3e809ab2a18d6e96e"
  },
  {
    "path": "deploy/helm/Chart.yaml",
    "size": 127,
    "sha256": "fa12bf5e22f5df7e74d43dacb73fc852f01ab089ee87b54ea02509753fecd498"
  },
  {
    "path": "monitoring/.gitkeep",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "docs/api.md",
    "size": 392,
    "sha256": "8838d452e2befda15dedb15c2f7d2110e48356ccd0fcd6457315f816b47d8502"
  },
  {
    "path": "docs/sqlite.md",
    "size": 98,
    "sha256": "428c75fecef3495b1a92a0f1abb31efcb40d1ab5d628a4b4de42ab0d75460e9b"
  },
  {
    "path": "docs/README.md",
    "size": 298,
    "sha256": "ec8e5c487a24359230502938e08581856b70f0d46d8cccc3b9978412dbe2c9c1"
  },
  {
    "path": "docs/deep_research_prompts.md",
    "size": 3592,
    "sha256": "ff2b54c464aa782b52f307faa4e7c1b016a49af79e290b10261dd8f06f7caf21"
  },
  {
    "path": "docs/ephemeral-runners.md",
    "size": 4459,
    "sha256": "2bf9d797bf7064e1c1d7837a5d1ba43ffa94ad39447173c6dd4af29bf2594fb2"
  },
  {
    "path": "docs/architecture.md",
    "size": 864,
    "sha256": "fc6ed8478f1dc36e1652e5f92dc0ca9b29a1161430943e82a9660942e1051623"
  },
  {
    "path": "docs/safety.md",
    "size": 1055,
    "sha256": "31c821378f9adedd83ac7717741d0d7cc6bb365e85e584bc817c06274ddb9eca"
  },
  {
    "path": "docs/patch-troubleshooting.md",
    "size": 1570,
    "sha256": "5e0fcbc51bf9cb614ed010465b78687517a1422bc8523bcf8903541901894149"
  },
  {
    "path": "docs/dynamical-system.md",
    "size": 7594,
    "sha256": "b6b6369b1d2aed3410193e68e734bda50fca03400a1ac75a9d8c5e71da47d215"
  },
  {
    "path": "docs/getting-started.md",
    "size": 1213,
    "sha256": "0bba2b859358ed3e09910c5e978fc3331454f20b58e9b1baf920b0535254478e"
  },
  {
    "path": "docs/requirements.txt",
    "size": 93,
    "sha256": "30775f5aff4e37ab82b44f3148e1f8c7a898a1a641586016657797a0c67c73b0"
  },
  {
    "path": "docs/tracking.md",
    "size": 487,
    "sha256": "f2a793c54220a0bfa0e6016181744023c8702b125283c1864ea8b978a4fb7e88"
  },
  {
    "path": "docs/concepts.md",
    "size": 294,
    "sha256": "5dff7173becd3efaefb80b64d9e2962be8ab43f8e75457b2f638fdd837c49207"
  },
  {
    "path": "docs/ci.md",
    "size": 968,
    "sha256": "603c553204986f3b4aedb3132d76919626231eb129ec9908d9e7a9f7f61a609e"
  },
  {
    "path": "docs/SOP_CHATGPT_CODEX_PRS_LOCAL.md",
    "size": 814,
    "sha256": "0585d2c92b21b8c45ae1ee39d89f9c09bab5043163124379ad65535a3cd1c026"
  },
  {
    "path": "docs/RELEASE_CHECKLIST.md",
    "size": 418,
    "sha256": "fd03c5ae5375de88f9bbc99afcb6065ff9c393486ee0ab21cf58043b4490bf54"
  },
  {
    "path": "docs/repro.md",
    "size": 120,
    "sha256": "c021f049d5542122286385c69bc1dd9d34ebe86ddb3d5cf6a37234a828126606"
  },
  {
    "path": "docs/index.md",
    "size": 306,
    "sha256": "98defe2bf0cc0077df27cf7c27515ad422998cf0f89a2bb1b929f637714f75e9"
  },
  {
    "path": "docs/dev-notes.md",
    "size": 1766,
    "sha256": "a19254a6d93c3c561b70649a56c2d6570a3d6b918439f4140624b8210626066c"
  },
  {
    "path": "docs/telemetry.md",
    "size": 102,
    "sha256": "a515bc001fb465a3e59d9bb240178e93b6bb5410aa30553b1411adfb4863796d"
  },
  {
    "path": "docs/status_update_prompt.md",
    "size": 3798,
    "sha256": "a35db5c4dda549bcbb27f627661ee2d274b7644273d848b5b3c9638d21a6f1f1"
  },
  {
    "path": "docs/modules/tokenizer_trainer.md",
    "size": 384,
    "sha256": "9e84e1c4086a9969711f9def8b67fa25da1235f94ecfa97afe8b0ba8a5fb88c6"
  },
  {
    "path": "docs/modules/plugins.md",
    "size": 1349,
    "sha256": "f7eb4ed6d1b05e39c6a3ac44f31f1a5317cdd562366f8de420afaadb2782a559"
  },
  {
    "path": "docs/modules/training_engine.md",
    "size": 502,
    "sha256": "529b05e8009c6ceed7d4dcf7331bc81892c5590c84c9b58a4b52894af72cd1a2"
  },
  {
    "path": "docs/modules/checkpoint_manager.md",
    "size": 372,
    "sha256": "b2f2e448ffc6fb81ca9e7d07810a245861177a4add1aeb59c706d16f262d82e4"
  },
  {
    "path": "docs/modules/evaluation_runner.md",
    "size": 451,
    "sha256": "93ec7ec92de24bf0b82969547c391b16015367f1fc97206e915a12300fbc5e36"
  },
  {
    "path": "docs/ops/grpc_parity.md",
    "size": 174,
    "sha256": "ff1aa4ac4003586c4235ae874c719440e924400d67a8b725d4717e449e23cddf"
  },
  {
    "path": "docs/ops/environment.md",
    "size": 271,
    "sha256": "093b66bb17c01e4e6bdab56e8422169aa940f935220e9ad5c2ae9b65803529be"
  },
  {
    "path": "docs/ops/monitoring.md",
    "size": 2099,
    "sha256": "a88158b490e57934505e75b7fcf3c74f782950516910456cb1bc850fbc2dda98"
  },
  {
    "path": "docs/ops/deployment.md",
    "size": 1069,
    "sha256": "5961da2bdb534df5be751a2a974284a6adf7f28c15cde083286109e0b01c7b89"
  },
  {
    "path": "docs/ops/experiment_tracking.md",
    "size": 2706,
    "sha256": "ad39861640634e93f0204402c01b422941b4f296101edb9ae797e530d0a6cc51"
  },
  {
    "path": "docs/ops/training_args.md",
    "size": 2026,
    "sha256": "0fefa26378edd2aff6446235c2bca453e4a27cce9b4c508d6a9eb663f10e51c9"
  },
  {
    "path": "docs/ops/ubuntu_setup.md",
    "size": 681,
    "sha256": "4b93dc93b25c639b76a738530cb01bfa24f82f50270e9c69f0dc2ce84898398c"
  },
  {
    "path": "docs/ops/hydra_distributed_overrides.md",
    "size": 382,
    "sha256": "0afb3da32d4dccd05d15a7d55ee58fcb2722b81b926a64deaf155177ec9d1aeb"
  },
  {
    "path": "docs/examples/model_card_template.md",
    "size": 166,
    "sha256": "632636ffb4955a4c74966ea1356742cc1cc5d743b8cfde9dedc8949e982c977b"
  },
  {
    "path": "docs/tutorials/end_to_end_cpu.md",
    "size": 267,
    "sha256": "a5f231716d7d3eaabe90a1e12eac27cc896dbf60f0a7b60d50ef9fdb1c8641d2"
  },
  {
    "path": "docs/tutorials/quickstart.md",
    "size": 213,
    "sha256": "45bf500f11ee86c0c7737f20ab478523d81b137da893688a16a3bb6e79f0e02e"
  },
  {
    "path": "docs/architecture/interfaces.md",
    "size": 1236,
    "sha256": "8642cdf6754dae9a46b52509d2dc12a8e190a88016f45c59d3b0fdf3b1a03493"
  },
  {
    "path": "docs/runbooks/offline_wheelhouse.md",
    "size": 3060,
    "sha256": "9cdab0dff7f275cfa17849e362be47b1e07839908fefbd5eafe4cc93332060c6"
  },
  {
    "path": "docs/model_cards/template.md",
    "size": 382,
    "sha256": "63cd4e0f248daa42d864fef039b99345ee665b6a50694721c6ea65a052de33f4"
  },
  {
    "path": "docs/dev/testing.md",
    "size": 771,
    "sha256": "2793cbd86ca114a52965a62cd198e112c7d82c7873360adbfbbf079c529cbb86"
  },
  {
    "path": "archive/removed/codex-ci.yml",
    "size": 1398,
    "sha256": "b1fa15f544aab27504b8736c906f52863ea322a39ec8f5a86394418e5e49554e"
  },
  {
    "path": "archive/removed/ci.yml",
    "size": 1691,
    "sha256": "10d790228c515c0e3b66185af2f5fbb3b44ae039d250e612052c3acea082a6f6"
  },
  {
    "path": "archive/removed/codex-self-manage.yml",
    "size": 1788,
    "sha256": "81c694ed944c1cd87e8e5481abe2c456f8ace8dc680f68b386cc7a45748d4e7c"
  },
  {
    "path": "archive/removed/codex-self-hosted-ci.yml",
    "size": 919,
    "sha256": "ccbe700d1448a78a1cd3ae2a77996f0b01ad5d20429fad6ce81fefae2265eb64"
  },
  {
    "path": "archive/removed/release.yml",
    "size": 686,
    "sha256": "fc7a9895fb6bc7a531ed31fd1b6e5e3f75c95cfff1c9f438e6a0f5cc29ea8f1a"
  },
  {
    "path": "interfaces/__init__.py",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "interfaces/tokenizer.py",
    "size": 430,
    "sha256": "a3fd48a88a98ffc05b0d10cc3a217546a2557f948ae64de1cc995ade7dbd320b"
  },
  {
    "path": "LICENSES/codex-universal-image-sbom.md",
    "size": 7878,
    "sha256": "7be24430523a1dc905f597200b9c08944051cddfeca034d8b8fb8c9e36fb3dd8"
  },
  {
    "path": "LICENSES/codex-universal-image-sbom.spdx.json",
    "size": 36165,
    "sha256": "f01f881af43a69cb75ce2fc90546e5dd493123e1a3a6efd1f38aea8d3f262c1f"
  },
  {
    "path": "LICENSES/LICENSE",
    "size": 2200,
    "sha256": "a3957f5993937f14ca56474ea28abdee9a37a999ac3773fbb65315108ba905ad"
  },
  {
    "path": "notebooks/quick_start.ipynb",
    "size": 5507,
    "sha256": "ed12198d7dbf70fa4d819b9a8ef30c9898c65281e28d61eb3faa213275cb6fb5"
  },
  {
    "path": "notebooks/gpu_training_example.ipynb",
    "size": 397,
    "sha256": "8963a72504c76ec53d872b7787fa8443099c35604a5cc5151a052617efdf2c09"
  },
  {
    "path": "examples/notebooks/demo_train_eval.ipynb",
    "size": 925,
    "sha256": "4356e51559d3d3347ead99a6dc77b45cc306e80c6653789a9aaec90977be27b9"
  },
  {
    "path": "examples/notebooks/demo_infer.ipynb",
    "size": 1029,
    "sha256": "70e6a5445da1008f143fedb1d0c9b159af9f78ed192e93e38521f9b2b7a6f570"
  },
  {
    "path": "scripts/session_logging.sh",
    "size": 286,
    "sha256": "9dd541fafe092cfb78b3b38862c2919ffc690ef797afb6ebe0bc7503d416e47f"
  },
  {
    "path": "scripts/make_quickstart_notebook.py",
    "size": 4116,
    "sha256": "1c99bd1c16d1c73e8bf3782aed2148875c6906cfa8bf9420182e4834ac79b7b0"
  },
  {
    "path": "scripts/init_sample_db.py",
    "size": 2913,
    "sha256": "1ea68e4f3e7ac06ba2eb06ee318720996f5dbad4cbaa3d4d4ddf7e1546d9d260"
  },
  {
    "path": "scripts/smoke_query_logs.sh",
    "size": 301,
    "sha256": "a209866bbdf0cf2c779084d5aae8e3905bec1c2ae8970967f82dcdae10a4e7b1"
  },
  {
    "path": "scripts/run_sweep.py",
    "size": 3340,
    "sha256": "19e47a0ab2b8b32bb72380aea191f055e3566e2ea11db667f3b76e10c36fc7e5"
  },
  {
    "path": "scripts/apply_session_logging_workflow.py",
    "size": 17944,
    "sha256": "23f1e967d939e008ddb25a505d462ec08e75ce560dc1880c71926bcc86780bdc"
  },
  {
    "path": "scripts/deploy_codex_pipeline.py",
    "size": 13264,
    "sha256": "82d8732d2c88693d245c6b403c98234cbec22ec5e37e849aaff2d2b8f33fab22"
  },
  {
    "path": "scripts/codex_local_audit.sh",
    "size": 2607,
    "sha256": "213c88656ab9c1c746a8dbfadde703784b753218b693dac5df71a8ecff9b6d0a"
  },
  {
    "path": "scripts/run_coverage.sh",
    "size": 135,
    "sha256": "991fa796e85ed3016835bdcf4678a09873a326b760572fe7d32b4d3bc213232c"
  },
  {
    "path": "scripts/run_supplied_task.sh",
    "size": 183,
    "sha256": "588811624a21200f828ca215c6e77eb85d4a094a43115b4927aa21c9ecc4fa67"
  },
  {
    "path": "scripts/build_wheel.sh",
    "size": 1502,
    "sha256": "11f93a8f0e94cf17c7ce8bad2babceb1cdf2725c610e4da35282f6a40837e135"
  },
  {
    "path": "scripts/codex_end_to_end.py",
    "size": 1535,
    "sha256": "28fb09d5601421e9d16b04af2ab34517814c4a0d519adf912fd0de703572c067"
  },
  {
    "path": "scripts/__init__.py",
    "size": 73,
    "sha256": "a9448c1a45e497aa875b52fbd8fb684452bf2fa192e8a597e8db92f020c72592"
  },
  {
    "path": "scripts/session_hooks.sh",
    "size": 3246,
    "sha256": "1d459d18928d31ae86cb3629459ac3653af544bd6b927c8d91af5d4ff323753a"
  },
  {
    "path": "scripts/deep_research_task_process.py",
    "size": 41627,
    "sha256": "de9776d36839816004706cc90caf64a7d816810bf2eace5871eb2d9925ef52a5"
  },
  {
    "path": "scripts/sbom_cyclonedx.py",
    "size": 659,
    "sha256": "0da28c4138c2c1f8806db59079da11ccefe6e4426aa68e575cc8075a12fbbeb3"
  },
  {
    "path": "scripts/smoke_after_build.sh",
    "size": 377,
    "sha256": "93da34511597364b412cae0a5f423d293cd65fb7e3cb1a7131dfcc4b3f42349f"
  },
  {
    "path": "scripts/benchmark_logging.py",
    "size": 2502,
    "sha256": "c24d9e1cd5f233312d4fdc95ac3f5bfda8e9a830dcb3d602f47d7a04a96c006c"
  },
  {
    "path": "scripts/archive_paths.sh",
    "size": 726,
    "sha256": "db50b525d204c29d4bf1cb56528eeb7a0b2de132ad3ee15990474acf421ae878"
  },
  {
    "path": "scripts/run_codex_digest.sh",
    "size": 2016,
    "sha256": "c40c096c2a6991f98325d72fa7aa07edc76d9f6de34995c993c02b9b5b644cf0"
  },
  {
    "path": "scripts/pre-commit-pytest.sh",
    "size": 410,
    "sha256": "eaa6e784b1dcdcf2f11dd7322b30e1b0e7fe4a4a7e5ae696eda249a92062852f"
  },
  {
    "path": "scripts/codex_precommit_dispatch.sh",
    "size": 4107,
    "sha256": "66441f87f9bd6e6fd9874ffdc291cb3877ef65d954965fe7dd55c5cc6d84d3cd"
  },
  {
    "path": "scripts/deploy/run.sh",
    "size": 532,
    "sha256": "e8dbf5b1ea9daaa0db5367ef572542f719f5a304fcf16270ecf562c4734eb2ce"
  },
  {
    "path": "scripts/deploy/build.sh",
    "size": 168,
    "sha256": "98a0a4c2995c968469575b08c4523f76bbf814aa249625ff2791ad6956ce7dfb"
  },
  {
    "path": "scripts/deploy/push.sh",
    "size": 293,
    "sha256": "1b1dd83981353353c6b633392edcc70a6b7cc1fcc57afa0271b57a337f675a75"
  },
  {
    "path": "scripts/env/setup_ubuntu.sh",
    "size": 791,
    "sha256": "1058048ef5dbe1472c4b677db215d44d51e98321f81043213ddf35e65ffc64e1"
  },
  {
    "path": "scripts/env/print_env_info.py",
    "size": 323,
    "sha256": "c65a80cc0c44c081af82f35d26b93d835dfadda5cdff5079db4fd67e84762f5c"
  },
  {
    "path": "scripts/env/create_venv.sh",
    "size": 537,
    "sha256": "e42ad0f16f1b8020b99390cbd223849d150a5f0e3d4bc348539f7ad3b3f82e16"
  },
  {
    "path": "scripts/gpu/check_gpu.sh",
    "size": 228,
    "sha256": "d0311fd151ace51c3dfd4b6608d13acafe5ac297735b8cfa4ab9596c38959214"
  },
  {
    "path": "scripts/cli/__init__.py",
    "size": 26,
    "sha256": "0207336f081098e8920fe695556de93aaf7bb9f3029a16af6d3e297bd01a3335"
  },
  {
    "path": "scripts/cli/viewer.py",
    "size": 1120,
    "sha256": "77b531142100a842f6b48a97a3de2c47a0027b1bcfc7785af65bb492e218aa78"
  },
  {
    "path": "analysis/providers.py",
    "size": 424,
    "sha256": "1a1df8958e79ae1a432c96896630a45a5d962de0117c340f8283c95f9952fb09"
  },
  {
    "path": "analysis/registry.py",
    "size": 402,
    "sha256": "5052049d935ed53897e94aab8131ca8fe8ee38d35f20c2cffb7c08cccfe0321d"
  },
  {
    "path": "analysis/audit_pipeline.py",
    "size": 3091,
    "sha256": "281074077c837646b0f1ce1056f02b3f5988c4660e2d222e396c3391a70b2b9c"
  },
  {
    "path": "analysis/__init__.py",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "analysis/metrics.py",
    "size": 441,
    "sha256": "85fc0caa139d0dd504e8f976e4b9149bbaa958477862777eb0332dc11e0e5304"
  },
  {
    "path": "analysis/parsers.py",
    "size": 571,
    "sha256": "cc66a5a0f977d7795b2fc3b7c9ddb6b23848638c7567371a18e5e86bf652043f"
  },
  {
    "path": "conf/config.yaml",
    "size": 243,
    "sha256": "17f834a566c522ffad663de4fa39219642caf9d31edeb0c993becc44b9d96342"
  },
  {
    "path": "db/schema.sql",
    "size": 810,
    "sha256": "013c0a690ac2c320795a0917006fe7e0d08297c90b18b4dbea16c78b62012780"
  },
  {
    "path": ".codex/run_db_utils_workflow.py",
    "size": 15842,
    "sha256": "6c6ab5ea4e451a90f8776e1d38946be8b118b2f76b145df9e727dabc47e8b382"
  },
  {
    "path": ".codex/mapping.md",
    "size": 1505,
    "sha256": "f2735cfb97fcf98ff04f0128e5cd4b5f5a81d9d4d7fb3ef9062267c8905b5061"
  },
  {
    "path": ".codex/README.md.bak",
    "size": 22085,
    "sha256": "aada06374032569c441e2d572ec0e6dee64ec3355d5dd736c9628e6ca02f2599"
  },
  {
    "path": ".codex/action_log.ndjson",
    "size": 128,
    "sha256": "495747cafa8f74f6f4446e766d1edcf26341c3469db3b44d509b166298e2d658"
  },
  {
    "path": ".codex/change_log.md",
    "size": 512748,
    "sha256": "aee49ffae790226f8a1c87446dc35f1ec0ea5faaac86d4404382dac0b12c4d9c"
  },
  {
    "path": ".codex/DO_NOT_ACTIVATE_ACTIONS.txt",
    "size": 42,
    "sha256": "8ce286b73ab6730ad094cdf41355f7662c16c9a02bd3cb2f1efa121f94575c2a"
  },
  {
    "path": ".codex/status.post.txt",
    "size": 26,
    "sha256": "94b64b1f464da62c5f5e2e665c9afbb2f036816c8deef6bdda8017eca3c0da13"
  },
  {
    "path": ".codex/mapping.json",
    "size": 569,
    "sha256": "4ed3844a720e885b24ad9b514a2f96e2880f11c57b65786526b72e313751e29e"
  },
  {
    "path": ".codex/inventory.txt",
    "size": 5111,
    "sha256": "22c1b82a20294ba64920c991a46856618020d8d07ff435813070f53d587e5cc6"
  },
  {
    "path": ".codex/lint-policy.json",
    "size": 69,
    "sha256": "5dfc5f8430a395c38f96a37d940ccce184834342ed55352dfe9752a0c2e2a29a"
  },
  {
    "path": ".codex/flags.yml",
    "size": 41,
    "sha256": "1d752c098264a3a2fd4f966e5f080d8eb2c720093a59b660acdbb16862dfb9ef"
  },
  {
    "path": ".codex/run_repo_scout.py",
    "size": 16952,
    "sha256": "e3e15a8a94a8dfe378cbd078a6fec52a690bfd8779b04dbe0eed687edbeecb42"
  },
  {
    "path": ".codex/inventory.md",
    "size": 6335,
    "sha256": "5d9af48f4e7e6009260ecb9c4bce81d1e82e82d38ab073e5730f23d2e0a5be73"
  },
  {
    "path": ".codex/mapping_table.md",
    "size": 364,
    "sha256": "27426d4c0b8ae7f6329f98977efbe7bc2c96e4f1e1417a76a5b7ae93758156f6"
  },
  {
    "path": ".codex/results.md",
    "size": 649677,
    "sha256": "582ffb64e289e0b4dee37f12a7f7e2bb74c1b6a450d28a719873f8a005feb40e"
  },
  {
    "path": ".codex/inventory.tsv",
    "size": 5706,
    "sha256": "99a88b1d93be6fc8995e8e54c66e5beafcaba031a0710dbe4d6576fdf003ddd9"
  },
  {
    "path": ".codex/flags.env",
    "size": 36,
    "sha256": "2d500245c68d4e6466dac82d814bc920a31fa5a70a48fe90f80ae9217913b77f"
  },
  {
    "path": ".codex/pre-commit.log",
    "size": 440,
    "sha256": "ee6075bee5f72c0a9802bcfa3510284c90891bf794d448d20b98b60856dd8c1b"
  },
  {
    "path": ".codex/guardrails.md",
    "size": 10996,
    "sha256": "d953c6342570f1271523f77bd8f4171ef51c33ce23d0645d63e4a0c98ce3ebb8"
  },
  {
    "path": ".codex/inventory.json",
    "size": 445,
    "sha256": "d944305bfd21fa662bc2e3c4b19401c6b3fd47b82cfe07b375c701c0553ce5ee"
  },
  {
    "path": ".codex/pytest.log",
    "size": 5133,
    "sha256": "0b026cb881e0e06f689424e0e5e5359a0c7b1d8e566d4ea1f5df8c2cbafd001d"
  },
  {
    "path": ".codex/mapping_table.json",
    "size": 2456,
    "sha256": "751437cb9affb27fe5bed5c55f1e0cb1dac1bd8662496e75195ef31170db77db"
  },
  {
    "path": ".codex/flags.json",
    "size": 118,
    "sha256": "e93f3441a9e065da5f1e64990aca2e8e89b670db79edae0021c27a102152dd81"
  },
  {
    "path": ".codex/deferred_items.md",
    "size": 511,
    "sha256": "f33148c4d8bba90de5dc705c9deaef0aa9c1deeb8d5843b97aff1471f9db77cd"
  },
  {
    "path": ".codex/inventory.ndjson",
    "size": 129,
    "sha256": "8074e8975fc932605e6199f7e60ffbeb667b9691f41e8ac50345ce838ee89ee3"
  },
  {
    "path": ".codex/smoke_checks.json",
    "size": 1797,
    "sha256": "f742466441e005c1d65fe5390a0f767537785d75d7e28d11865d72c2af039f18"
  },
  {
    "path": ".codex/ruff.json",
    "size": 44152,
    "sha256": "fe54fa2c82607923f8c1314f0b4c86787e5548c4a29a88288abd28b1e642a649"
  },
  {
    "path": ".codex/DO_NOT_ACTIVATE_GITHUB_ACTIONS",
    "size": 50,
    "sha256": "4186f013a2a53b59def4c732dd96067fc01e232c0b527c378676196a220c9419"
  },
  {
    "path": ".codex/run_workflow.py",
    "size": 16783,
    "sha256": "ab6b7231a90c2bf91872aea54a6fb5376d38bd8c1a1aac1c66f5857807842236"
  },
  {
    "path": ".codex/search_hits.json",
    "size": 1481,
    "sha256": "85f214bc010fc80be713ae53b60d39bea760fb39738cda45f44e25294bcedac3"
  },
  {
    "path": ".codex/codex_repo_scout.py",
    "size": 18378,
    "sha256": "99d76b5d978a6101699322ad9e41403de5a9526dc78c2ace4e37860aeb3e2350"
  },
  {
    "path": ".codex/errors.ndjson",
    "size": 127,
    "sha256": "759dd2bc64496d7b7f4ed1e9fa0cc330c75a12d3d978fc71d5b2bc5ecc857eba"
  },
  {
    "path": ".codex/status.pre.txt",
    "size": 25,
    "sha256": "2f17b164b2bed1575878814ad07010c984d43e3c54b0336dcd2947abdef2116e"
  },
  {
    "path": ".codex/hydra_last/config.yaml",
    "size": 279,
    "sha256": "eb86d89bd72c7ad61d325a0321a6e2c61a292d8d8948311132fbaa1b98e1998d"
  },
  {
    "path": ".codex/smoke/import_check.py",
    "size": 2465,
    "sha256": "17775cc914fa1794641f3d7c1340509dedffd45f35f35d8895fe5871eb67cfdc"
  },
  {
    "path": ".codex/automation_out/change_log.md",
    "size": 2880,
    "sha256": "172c2bad659e00c1e8ec0217fb9f8136ca3bbe2f268be35bd25688ea6f6603d3"
  },
  {
    "path": ".codex/automation_out/db_catalog.json",
    "size": 3,
    "sha256": "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
  },
  {
    "path": ".codex/automation_out/coverage_report.json",
    "size": 467,
    "sha256": "49d731215488a2a8d3a630f8c8bc2484ad6f0935c50cdb4ba6b897c9c6ec6d50"
  },
  {
    "path": ".codex/automation_out/db_inventory.json",
    "size": 69,
    "sha256": "a765d3fd7b0458ce7d099db0be1b5179939a17c70ef4084c2d707f1d85133b39"
  },
  {
    "path": "patches/changelog.patch",
    "size": 759,
    "sha256": "3f596d2e70a08f55103026df9f4bd639b57aca53bfd99cacbe5e048c438e956d"
  },
  {
    "path": "patches/workflow_codex-ci.yml.patch",
    "size": 370,
    "sha256": "b3ba7c3ed960d404760e7cfe51aab0bcbdc9ff747f997a88dac3b73048690e11"
  },
  {
    "path": "patches/analysis_audit_pipeline.py.patch",
    "size": 2489,
    "sha256": "9a69e3a7fbb6e9a3b06624194c3a8367b2b812336f550223ad0d60d379e934ed"
  },
  {
    "path": "patches/analysis_parsers.py.patch",
    "size": 595,
    "sha256": "bd76e948e60e8f7061b33d4902f9e5c3ae6bf5d92a99449e30d0310c7c1cfb9e"
  },
  {
    "path": "patches/analysis_metrics.py.patch",
    "size": 465,
    "sha256": "6a1609cd6f5d1b8a5e6211a665d5f0854e78cde752559933909363a17d404500"
  },
  {
    "path": "patches/readme_offline_block.patch",
    "size": 709,
    "sha256": "76397eef1ef84b6d1a64ca35bbbe5fd0cf5b32764e68adb715b930ae2a768f10"
  },
  {
    "path": "patches/analysis_registry.py.patch",
    "size": 427,
    "sha256": "7bfa285097086f415f4c7d2e1fc75ef697b7cf5f3b79a8cdb482be87f15b6813"
  },
  {
    "path": "patches/ci_local.patch",
    "size": 671,
    "sha256": "b652c8f0dc34be48fb719043424b0cdcb3d66f5b9cd4909a3d366b0d4a59a3c6"
  },
  {
    "path": "patches/analysis_providers.py.patch",
    "size": 450,
    "sha256": "3147a69f291004bffaa24add0906c2539844a8ef4d6da1fd0cf64848f7cd7498"
  },
  {
    "path": "patches/workflow_codex-self-hosted-ci.yml.patch",
    "size": 429,
    "sha256": "a2d10aef6f0753c8ce76549eaaa64f6bce1f58483de53f5093c961570e8e3a6a"
  },
  {
    "path": "patches/analysis___init__.py.patch",
    "size": 25,
    "sha256": "43d5c4cb9e58ca3754aababe3f38d26bd6e3f76aa45fe22cde474bf71557a126"
  },
  {
    "path": "patches/analysis.patch",
    "size": 21283,
    "sha256": "61ed816ef5ca7ce39897ae0833aecdcb5a5c1c408c2c75fe3effc3a171d935f3"
  },
  {
    "path": "patches/workflow_ci.yml.patch",
    "size": 358,
    "sha256": "18aecab6c384fe93fc74f513e2b290d06f0784cc0f53277f07c7ad64d4668e3a"
  },
  {
    "path": "patches/workflow_codex-self-manage.yml.patch",
    "size": 406,
    "sha256": "afe7117ee6db23f5b17aa7affbe39486fcb8a14f66410f0b356bd466e46fff15"
  },
  {
    "path": "patches/analysis_metrics.jsonl.patch",
    "size": 705,
    "sha256": "8bedb8a64ac6dc85e6b99dff33ebd9a7240c79c5662701f7f2f018e4b22f4c79"
  },
  {
    "path": "patches/workflow_release.yml.patch",
    "size": 648,
    "sha256": "c9f741ad64be1e9fbc11a0995391ffd359900b433f3f980c764355edc3301b4b"
  },
  {
    "path": "src/logging_config.py",
    "size": 485,
    "sha256": "d3be844b7b6d1cd88f17e77213ede27d4580ea1cacd7a299261c4ff4dc58c830"
  },
  {
    "path": "src/__init__.py",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "src/data/.gitkeep",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "src/codex/chat.py",
    "size": 2794,
    "sha256": "27d8b86144687738f52aa7bdb6a0e74013b9e2129cdb8e1a6e4da734ee9f48f4"
  },
  {
    "path": "src/codex/__init__.py",
    "size": 125,
    "sha256": "2cf2ed614e197bf01a62fc61f6178bacc80e8432f673719765fcdaa8a8bfb51a"
  },
  {
    "path": "src/codex/cli.py",
    "size": 7456,
    "sha256": "b92098720789b80f5e0d8dee105d6f8b9e75b47a5099b333eed307f37a756c27"
  },
  {
    "path": "src/codex/monkeypatch/log_adapters.py",
    "size": 1877,
    "sha256": "393bc4202ccb9c48f4855dd795cc731b3460837a30ac5af20e715e1b56160e87"
  },
  {
    "path": "src/codex/logging/conversation_logger.py",
    "size": 3591,
    "sha256": "7b962a1117c1ba6a2adc8ad1cff1e9c76c8882cc504a8c78b4b5ade598c32e6b"
  },
  {
    "path": "src/codex/logging/fetch_messages.py",
    "size": 2629,
    "sha256": "f82fc09389c372211769cc97b2d587b46fe029627e92c0026035ef7514399239"
  },
  {
    "path": "src/codex/logging/query_logs.py",
    "size": 9314,
    "sha256": "504d89a4e6cb9e56dbba58df7216e6837a8795f90f54a27c60587a4b1dcebbf9"
  },
  {
    "path": "src/codex/logging/export.py",
    "size": 4189,
    "sha256": "2bb58ac363ffaf301d406ccf66b09e833196f7917e5fe3a2af9fe505d5f7ca06"
  },
  {
    "path": "src/codex/logging/db_utils.py",
    "size": 4897,
    "sha256": "8bdd7f17107efdac9e6b7a6cfde133f8c7deacf5b7a159a35e6b474b00485db3"
  },
  {
    "path": "src/codex/logging/__init__.py",
    "size": 556,
    "sha256": "b0331f7580c77769ee9540462989aa29bafe1c03e49b069857661a021615e186"
  },
  {
    "path": "src/codex/logging/viewer.py",
    "size": 8720,
    "sha256": "52834e6ccc500bced402e1557d9d1b90c7102bf79baf982423317611dba9efbf"
  },
  {
    "path": "src/codex/logging/session_logger.py",
    "size": 12658,
    "sha256": "646bf1b4f0d53a2eeb21d81ea40106d077c17d502331575576d8af531ab3719f"
  },
  {
    "path": "src/codex/logging/config.py",
    "size": 360,
    "sha256": "4cf542f7e9697e45f9322125365843a985fb3d912fb02cfea9ff05b08c26c1d0"
  },
  {
    "path": "src/codex/logging/session_query.py",
    "size": 7154,
    "sha256": "ae22c75e06676c089c95453da9588ffea4def4571292f7e1487fb94f12d09fcf"
  },
  {
    "path": "src/codex/logging/session_hooks.py",
    "size": 7647,
    "sha256": "c953427ba87fe5db4f1b59dfc39be901c32b55b4284f054cffa5267aa8c6cd66"
  },
  {
    "path": "src/codex/logging/import_ndjson.py",
    "size": 8999,
    "sha256": "bcd3fd389e6433cf043b3c44dac26481f5e7398df06b04ea34a9a28ab674260a"
  },
  {
    "path": "src/codex/search/providers.py",
    "size": 3918,
    "sha256": "7b89f97f1e2c4f5cad989b81845aa3243b4b0d80b65385a7e7dbf213ba09a51e"
  },
  {
    "path": "src/codex/search/__init__.py",
    "size": 278,
    "sha256": "e0788857651c6220ecc3d2424fbd572abc4d3bd98ac78cb3ce1a44c35783d37c"
  },
  {
    "path": "src/codex/db/sqlite_patch.py",
    "size": 4653,
    "sha256": "77354c72a4228a55a20f19a76b7b074fbc5dd09d1f1377f9335766d4ea776a2d"
  },
  {
    "path": "src/codex/utils/subprocess.py",
    "size": 719,
    "sha256": "4dc74a361040913bf51bd3090b6e3a85565346fb4a0d1d2876f60a6d9d360ef7"
  },
  {
    "path": "src/codex/utils/__init__.py",
    "size": 33,
    "sha256": "a92185684449687cb4f3ee7b0af3807ab422ec5f0995a9132c8c32bff77d1fe6"
  },
  {
    "path": "src/ingestion/README.md",
    "size": 615,
    "sha256": "f507881a0f97500fe2d54f7918481cfbd921f573453b748160eecf831dd30409"
  },
  {
    "path": "src/ingestion/io_text.py",
    "size": 5222,
    "sha256": "509cc73a426becefba8621d2f0ac7bc5b4e31b6c48f06667d1fd28eb8fe3a13d"
  },
  {
    "path": "src/ingestion/encoding_detect.py",
    "size": 5409,
    "sha256": "cecd52ed66614a0e1721ad780595ca6297c9ad0dfe2ca73961d07308dd04feed"
  },
  {
    "path": "src/ingestion/json_ingestor.py",
    "size": 640,
    "sha256": "ff27d4e73d5825def1650eabbc24cefe712c8103a0d84f457495ebf048ee16c4"
  },
  {
    "path": "src/ingestion/file_ingestor.py",
    "size": 604,
    "sha256": "ebaa60e48ac665d7e7a8a7672cc864c17a13b800ed237683064750063d5193ae"
  },
  {
    "path": "src/ingestion/__init__.py",
    "size": 10657,
    "sha256": "f94b15feb7bcb516c77f53b10c0b021be5b915293ba06906630d45e7ba5ac8db"
  },
  {
    "path": "src/ingestion/csv_ingestor.py",
    "size": 796,
    "sha256": "b15631d58a287ba5164d9ad405a637ff85f2cc62a208933463d0c814752caa02"
  },
  {
    "path": "src/ingestion/utils.py",
    "size": 11027,
    "sha256": "acb65ea8f3dffc2fbcb1afce2e0a279de411d5750c7d9512843d961f3bf9396e"
  },
  {
    "path": "src/safety/.gitkeep",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "src/tokenization/train_tokenizer.py",
    "size": 4407,
    "sha256": "040e5e5708d4f10d78432e5c9d965eca00a1a1e101327d5d704980b17d3369d4"
  },
  {
    "path": "src/tokenization/__init__.py",
    "size": 140,
    "sha256": "f139d42439612edf648a331b3cb3d47d5499030344ed8922b984b6b4277962f7"
  },
  {
    "path": "src/tokenization/cli.py",
    "size": 2035,
    "sha256": "bd3e138b26d3bc7b91fed32066ee845c9040ca814d021bd0798039fe14e81ba2"
  },
  {
    "path": "src/tokenization/.gitkeep",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "src/tokenization/sentencepiece_adapter.py",
    "size": 1690,
    "sha256": "5b260d2ff5aa0ae35d57a7f945155122c9bcb2b781ef329e9ed724b823efb7b7"
  },
  {
    "path": "src/codex_ml/data_utils.py",
    "size": 2696,
    "sha256": "315fba61af2482596716825c23604c3664749cf326c06a2ebc3583b63eba4bff"
  },
  {
    "path": "src/codex_ml/registry.py",
    "size": 236,
    "sha256": "6983b2f5033f26e2b4fb2bdd2e00a7dcbbfd379cd29cdc77e223bcbd9082c099"
  },
  {
    "path": "src/codex_ml/pipeline.py",
    "size": 2276,
    "sha256": "0edd9a1c9c46708da468bad64f9929cd078423f3d92d908d74d89538fc69db58"
  },
  {
    "path": "src/codex_ml/__init__.py",
    "size": 1226,
    "sha256": "5f4a89492e496c58f9e05bb6785c10e612e768ff43d5ff3c86ca5e060bdb2b02"
  },
  {
    "path": "src/codex_ml/train_loop.py",
    "size": 4128,
    "sha256": "88f8d37030efaff768b4c758c7ed1f8aa58a9324e32ab844c28fa3e0fc3882ab"
  },
  {
    "path": "src/codex_ml/symbolic_pipeline.py",
    "size": 17070,
    "sha256": "b02cadc78dc903eb86c8d455af5730036eb229dce0b5f2a56551bdd42a8d43bc"
  },
  {
    "path": "src/codex_ml/config.py",
    "size": 835,
    "sha256": "bff397da7bf224511fca42e542c543a30bfc60e51d3797fcbd93dd114268ed6f"
  },
  {
    "path": "src/codex_ml/config_schema.py",
    "size": 1568,
    "sha256": "68537588041628cfd9f990b73a90144bd972a702af4190a5eca982d634ce95a8"
  },
  {
    "path": "src/codex_ml/models/generate.py",
    "size": 2174,
    "sha256": "8c19c5bef2ec4b9a13b3643fdf03745a46d6f9b9489888d15915b16b28950d77"
  },
  {
    "path": "src/codex_ml/models/minilm.py",
    "size": 3104,
    "sha256": "5236ec4d034214680ab0027c466660533a83b0dbf85c4cd6179d867e55167283"
  },
  {
    "path": "src/codex_ml/models/registry.py",
    "size": 534,
    "sha256": "d79194218ee74363b23f199c0e51e7c44d6500515667bb103ec82bcd45a519e3"
  },
  {
    "path": "src/codex_ml/models/__init__.py",
    "size": 1819,
    "sha256": "127ceeb18ea727a46011c1c69f51adbc43a3d9f6bd685fea8a3330cc2f82896a"
  },
  {
    "path": "src/codex_ml/models/activations.py",
    "size": 887,
    "sha256": "2f077662e48b5ad126329e1ea44d8deeffbc568924e22a5a105b14477183d0ee"
  },
  {
    "path": "src/codex_ml/models/decoder_only.py",
    "size": 8879,
    "sha256": "4eaa775f3beeb7245371d67a394c95c68a04b9e33eb29f50dfa7f3a6bf266d78"
  },
  {
    "path": "src/codex_ml/data/splits.py",
    "size": 653,
    "sha256": "e68c78a862823302a82888068e6fa87c8a814973208f4aa853103152ecd4766a"
  },
  {
    "path": "src/codex_ml/data/sharding.py",
    "size": 342,
    "sha256": "674ef891e0890df59ee9e89e33883e6976a50849639b99c8f0bf97fce83b3190"
  },
  {
    "path": "src/codex_ml/data/__init__.py",
    "size": 220,
    "sha256": "05cee0ac236e5370fbd05670c3c957123d3b5829c51bc02367c67593dfbf86bb"
  },
  {
    "path": "src/codex_ml/data/cli.py",
    "size": 1497,
    "sha256": "6951ed45f6017cacb1bf032f09615df4a6ca16fed1bf4885dfc41ab5f5ae6c8c"
  },
  {
    "path": "src/codex_ml/data/cache.py",
    "size": 630,
    "sha256": "a96a26a5e572d920ffea35bbcb52ff50a461822992caea027265cffd3035e092"
  },
  {
    "path": "src/codex_ml/data/loaders.py",
    "size": 7860,
    "sha256": "3e001c270b7de96d5d705948d9087b63a9106b9edaaff3bfc34732e891494e07"
  },
  {
    "path": "src/codex_ml/monitoring/async_writer.py",
    "size": 4338,
    "sha256": "2a355166e97363ea28262fdea92273464bfbd0c95bc7a08ad8e1252792436faf"
  },
  {
    "path": "src/codex_ml/monitoring/__init__.py",
    "size": 15,
    "sha256": "2a8e5734a3d3e126632f9322366872b91f57570f5fe9f41ac7dac06af3eb7a9b"
  },
  {
    "path": "src/codex_ml/monitoring/cli.py",
    "size": 1475,
    "sha256": "f10dbcfac4f2f2d76b017215b41020463af028e8c22d09678d84e16d296363d2"
  },
  {
    "path": "src/codex_ml/monitoring/codex_logging.py",
    "size": 10736,
    "sha256": "6c0806d95f79112ef43e217354b4676b3ffe0275f47cfb1d7176e7c09db0676b"
  },
  {
    "path": "src/codex_ml/monitoring/mlflow_utils.py",
    "size": 2290,
    "sha256": "eb2e8edc1f18615231f9d5c07d30d9f272f8820259eaecd666f524f0ea6f9cbd"
  },
  {
    "path": "src/codex_ml/monitoring/prometheus.py",
    "size": 467,
    "sha256": "b4f86ebe6249a7c10391a4bf36480b03f682545e342febc762d9383b41e306f9"
  },
  {
    "path": "src/codex_ml/monitoring/schema.py",
    "size": 1660,
    "sha256": "59647ece5fd71c31642ad5cc0804ca3e85ac24ebdd98c2bdc688c3a2906b7079"
  },
  {
    "path": "src/codex_ml/modeling/__init__.py",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "src/codex_ml/modeling/codex_model_loader.py",
    "size": 3525,
    "sha256": "b415a2434d27112e68fa3f1d786764d43d2a4031f4e0c36d300df4c5173e18a1"
  },
  {
    "path": "src/codex_ml/interfaces/reward_model.py",
    "size": 1214,
    "sha256": "a7fa95b312de2ff507a3162664438973697bc77a0771c20b83d43e6a93dabbaf"
  },
  {
    "path": "src/codex_ml/interfaces/registry.py",
    "size": 976,
    "sha256": "2db5dbe9eca9eceabfbb6acb18bc50c9e4eeee1e6f427cb1f9783e53d0935370"
  },
  {
    "path": "src/codex_ml/interfaces/__init__.py",
    "size": 320,
    "sha256": "74c0d9d4f0f7ea229252d66d8b5690f4a38f6c0c0f0977211e3366b37485f5dc"
  },
  {
    "path": "src/codex_ml/interfaces/tokenizer.py",
    "size": 13956,
    "sha256": "56efee4e14f1042a1a9205c5b8b150f238d1a2a9860c2025baaa16369f6c62e8"
  },
  {
    "path": "src/codex_ml/interfaces/rl.py",
    "size": 854,
    "sha256": "4d7845304674d8768b579ba2526bff3d812c5acad53cd5d87f38e8b44f8bed7a"
  },
  {
    "path": "src/codex_ml/plugins/registry.py",
    "size": 3502,
    "sha256": "4407fcb5d1ce768c725de88cce092f2c9b454dbbfc53d4ff7d90f3c3ba070174"
  },
  {
    "path": "src/codex_ml/plugins/__init__.py",
    "size": 768,
    "sha256": "87b792903c5408f3cb6e98b9253b9ff50d394051865ed0e95654abf0345617b0"
  },
  {
    "path": "src/codex_ml/plugins/registries.py",
    "size": 1659,
    "sha256": "e70e28ce3dc2c8bdcdb73c31af4efb088df80dfdd6a2a33f6b8f7942859cf795"
  },
  {
    "path": "src/codex_ml/safety/sanitizers.py",
    "size": 2476,
    "sha256": "510d34562675cda51fce502fb32ceb2b6a8c928ca4367df21efcaf6548b86b20"
  },
  {
    "path": "src/codex_ml/safety/risk_score.py",
    "size": 1858,
    "sha256": "d6f6822d1ff8f996207f9d65e772a853d1cf28bf97139001285e4c0e955b72f4"
  },
  {
    "path": "src/codex_ml/safety/sandbox.py",
    "size": 2228,
    "sha256": "7e34469aa1e6fd0d02a86e2d909efc730fb927d889ad138fe91abc1db274c08a"
  },
  {
    "path": "src/codex_ml/safety/__init__.py",
    "size": 381,
    "sha256": "a530bb816c3ce59f692924b31bc5a3b2573715ce11b5994d9b9d4e543f8bae4f"
  },
  {
    "path": "src/codex_ml/safety/filters.py",
    "size": 3655,
    "sha256": "5114e27ed63e5d532347b238c36969f02cb409da00e66d2db3fcc7f1c16d335e"
  },
  {
    "path": "src/codex_ml/tokenization/train_tokenizer.py",
    "size": 2475,
    "sha256": "e2a870854c744da71d214ed30a54ccdb8b228fb637bc00b875c129752c93af13"
  },
  {
    "path": "src/codex_ml/tokenization/__init__.py",
    "size": 2208,
    "sha256": "414c66380e9df1deaf54981c6c078ef1ed9abd8e799571ad4c664b7761be269c"
  },
  {
    "path": "src/codex_ml/tokenization/cli.py",
    "size": 2424,
    "sha256": "edd2fee6e15bbc107f57e8f0d1d0c8d5e1f36beb3401cb662c915ee1462853a2"
  },
  {
    "path": "src/codex_ml/tokenization/sentencepiece_adapter.py",
    "size": 3935,
    "sha256": "213d5927f08108a49deca13b9d7b38be3464ca46e4106a18897818de8d317147"
  },
  {
    "path": "src/codex_ml/tokenization/hf_tokenizer.py",
    "size": 4891,
    "sha256": "a721e2cd4b14e9d07833d6e7231a44088c6f41fa1b0abebe461b834e0b21917f"
  },
  {
    "path": "src/codex_ml/analysis/providers.py",
    "size": 1374,
    "sha256": "908469be92ecca878cc9f1fcc0d759bd259557da5780c778fe447ff4756710b2"
  },
  {
    "path": "src/codex_ml/analysis/registry.py",
    "size": 1041,
    "sha256": "805a0f2d534a3056f7ee827e49973fd2f48d40141a7b2603697609c7225b149b"
  },
  {
    "path": "src/codex_ml/analysis/extractors.py",
    "size": 4354,
    "sha256": "21df8627786f42e70194f3d46687495c92aa3cda22159fec9e92ccd1bd949c3c"
  },
  {
    "path": "src/codex_ml/analysis/__init__.py",
    "size": 157,
    "sha256": "33eb9cb9b8bb2f5214a512e0b6f2f7ac6b1937aa61b5e77617208cf1a940e7a7"
  },
  {
    "path": "src/codex_ml/analysis/metrics.py",
    "size": 614,
    "sha256": "9df2ba0b8795789c87646d3dd615df5a3b5b6f5e1b4a3773289c0a2057825599"
  },
  {
    "path": "src/codex_ml/analysis/parsers.py",
    "size": 1430,
    "sha256": "9662b93e3fffffdf56e5a05a6da4dfc940ac6ffde65c3a6f16b5f8a7892ef76a"
  },
  {
    "path": "src/codex_ml/reward_models/simple.py",
    "size": 804,
    "sha256": "39f86b6d28b680870a0752d02f325da5b263ed4360e4ded42eb6ad532a5c4d79"
  },
  {
    "path": "src/codex_ml/reward_models/__init__.py",
    "size": 117,
    "sha256": "e6d7bcd9f1b7b0d640870c27b5001164c07bc714b146b625c206348cc028d9df"
  },
  {
    "path": "src/codex_ml/tracking/init_experiment.py",
    "size": 4003,
    "sha256": "f13f32f2259a98694127c67e819612f657e841a297ce3f0475acfe64d389b830"
  },
  {
    "path": "src/codex_ml/tracking/git_tag.py",
    "size": 1115,
    "sha256": "f11579fc83418babcbb628c0447ec6389edcb361e735667ac336863d82ff5ab1"
  },
  {
    "path": "src/codex_ml/tracking/__init__.py",
    "size": 487,
    "sha256": "7a1e78319d5ad3b4e8c846ebd9105310025a2b6e9c261f64ab730ff6d60c5a2a"
  },
  {
    "path": "src/codex_ml/tracking/cli.py",
    "size": 999,
    "sha256": "1b7a9414b79bbe70ef8f5207a5d93cd4a77f11edb97665622d298db5085e9533"
  },
  {
    "path": "src/codex_ml/tracking/writers.py",
    "size": 4939,
    "sha256": "59d99aeddcdff398a703a844495230c875e51abc75fa680643f6df3127c320a1"
  },
  {
    "path": "src/codex_ml/tracking/mlflow_utils.py",
    "size": 11676,
    "sha256": "e8ec3cf421cbbd098bba206b5b539988429c16c5e0e8bcbd4bf547c6496e50e8"
  },
  {
    "path": "src/codex_ml/metrics/text.py",
    "size": 630,
    "sha256": "a9e456af484d303387d14ddbac41cb7081434df78d7b089c134c4a32b29de887"
  },
  {
    "path": "src/codex_ml/metrics/registry.py",
    "size": 7087,
    "sha256": "dfd3743903da80caa11e7cfb41da8e77d25bc1d0c7b5746f9964e529536a301a"
  },
  {
    "path": "src/codex_ml/metrics/curves.py",
    "size": 795,
    "sha256": "0151ee801807480c9e2c34360ddf81071e733ef80495bae8010933d03afa7dca"
  },
  {
    "path": "src/codex_ml/metrics/__init__.py",
    "size": 126,
    "sha256": "c891cdc1b403642095979b7447e2ab66e5a70bbe5b0141548f52b04b957a4be7"
  },
  {
    "path": "src/codex_ml/utils/provenance.py",
    "size": 2194,
    "sha256": "668012cfd73a82fb0ebaaa00ceef2199c1139781c6c89a85bca03c6634313c79"
  },
  {
    "path": "src/codex_ml/utils/seed.py",
    "size": 664,
    "sha256": "b57d9d085a4bd337bd9623986c7d689bf63d9e889d3c1020de5371cbc7541b63"
  },
  {
    "path": "src/codex_ml/utils/checksums.py",
    "size": 501,
    "sha256": "563dd688ddda225b026485082ccdf91df8f8aacdfcca4c12ed23c85f5bd5bc73"
  },
  {
    "path": "src/codex_ml/utils/modeling.py",
    "size": 1415,
    "sha256": "1ed9dfa8c74c926aae0f3dbb6cc809bb767dab66cc564eeaa5a01c6eaa0beb92"
  },
  {
    "path": "src/codex_ml/utils/error_log.py",
    "size": 1579,
    "sha256": "22fddbe8894ab3c13102484a313e950e0ea7d10d92bbaf278d0c56409b7cc17c"
  },
  {
    "path": "src/codex_ml/utils/repro.py",
    "size": 1846,
    "sha256": "de1465d9a3c86690b715dde744d0366292ab88dee66f3caaf66af2a563cafa9b"
  },
  {
    "path": "src/codex_ml/utils/checkpointing.py",
    "size": 21112,
    "sha256": "730dbc92a6c147d13515f21a7683e803114c3cfd1e71070a99667287ae4b312f"
  },
  {
    "path": "src/codex_ml/utils/__init__.py",
    "size": 243,
    "sha256": "827a2439e89302e031fa6f7c6784f4bc3be7d7884bc252d1cf29f1e25b64b86c"
  },
  {
    "path": "src/codex_ml/utils/config_loader.py",
    "size": 2146,
    "sha256": "538c2cf995d1a3182bd7dbb627139e9e5162e4de611715c1930a1c975ea9135d"
  },
  {
    "path": "src/codex_ml/eval/run_eval.py",
    "size": 3061,
    "sha256": "344b9707ccb970588c6ceefa7e9c9de2501f3500e524efe1c547a2b7a5f18c11"
  },
  {
    "path": "src/codex_ml/eval/evaluator.py",
    "size": 1318,
    "sha256": "0a7fde3585ea2c6e0224ce27fdabadb09fea599c7d7502122cc540f78b3619c7"
  },
  {
    "path": "src/codex_ml/eval/datasets.py",
    "size": 5967,
    "sha256": "215ec1fa9110e867ae04cb240f2c5773dc51f9bd09ace41ca1ff9acd029e5b61"
  },
  {
    "path": "src/codex_ml/eval/__init__.py",
    "size": 94,
    "sha256": "4b4a6609b8455c07db9307b7e496a28250f27ff6fe24dc36a2422f67cb93a23f"
  },
  {
    "path": "src/codex_ml/eval/metrics.py",
    "size": 5429,
    "sha256": "ed2202089b742fd90601ee7d7a0c56416c1caff31a7e5768192ef66f420d4b89"
  },
  {
    "path": "src/codex_ml/eval/eval_runner.py",
    "size": 4503,
    "sha256": "e7a3dda6defad8c9051d4366641783c23641b5aae9a19da26d1b307c0405d2c5"
  },
  {
    "path": "src/codex_ml/peft/peft_adapter.py",
    "size": 5199,
    "sha256": "8debe316a3920c29d7bbd7228750dc3a69e092d2f12adca321cdf4e3febeab6c"
  },
  {
    "path": "src/codex_ml/peft/__init__.py",
    "size": 12,
    "sha256": "e449e6e7e884d78626fe5c31a699e8412b307206842c69e12cdf1b36b442a195"
  },
  {
    "path": "src/codex_ml/cli/generate.py",
    "size": 2050,
    "sha256": "bf2704c2abd72a5a1beaa8f7972b2b3bc8c7d1cd1fdf2d2b969771b3459164bc"
  },
  {
    "path": "src/codex_ml/cli/audit_pipeline.py",
    "size": 4661,
    "sha256": "8aeff7f39b862d9c625b3464ec47cf75ab9c45ffb03b4bdc920a8c11a752ca46"
  },
  {
    "path": "src/codex_ml/cli/plugins_cli.py",
    "size": 1844,
    "sha256": "6143fb6a8fbd084a965c4627d90ab9a98c37163deb2cc0f6dae1d9d78cd8c122"
  },
  {
    "path": "src/codex_ml/cli/infer.py",
    "size": 3219,
    "sha256": "d4d4fa329de1bdc7fc1c64fffb92be9f33e283977625ef955cd89cf296a604d5"
  },
  {
    "path": "src/codex_ml/cli/main.py",
    "size": 2845,
    "sha256": "77238d3bc85ecd45100c3ecb3da8ec87d99ac13f9d4259db14dcf7bfc0af6177"
  },
  {
    "path": "src/codex_ml/training/callbacks.py",
    "size": 1307,
    "sha256": "2cc548b662da06025c8133e89ad343de7213b4fbfc7023f0561e330d6584c8f9"
  },
  {
    "path": "src/codex_ml/training/__init__.py",
    "size": 13,
    "sha256": "a94b732c00daa4041b20cee2b749bde32151ff9c2691f3b804173f65a14687d7"
  },
  {
    "path": "src/codex_ml/training/functional_training.py",
    "size": 5176,
    "sha256": "a430bb3d653c262b7df8ca8df9fd2e3724b73670b905e7edb2ff26e1277614bd"
  },
  {
    "path": "src/utils/training_callbacks.py",
    "size": 1160,
    "sha256": "dc11fb5c553c48e3a8645b460b52a52bd07514a5d850a123ba743696913f2f0d"
  },
  {
    "path": "src/utils/trackers.py",
    "size": 865,
    "sha256": "c9f9a4db81d023f66e099c8638526b84ebb63915f6f9f79713eecb23ce369a31"
  },
  {
    "path": "src/utils/checkpointing.py",
    "size": 6038,
    "sha256": "9c51766123a326b04fe03147c32920e0355478d2f9b14af575675a301dc89947"
  },
  {
    "path": "src/utils/__init__.py",
    "size": 275,
    "sha256": "8c21bce83b3cb17b9179a77c3cb520776b48ea9d89ff8742ed8639c87865e384"
  },
  {
    "path": "src/utils/.gitkeep",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "tests/test_session_query_cli.py",
    "size": 1373,
    "sha256": "f88461ce7a9609b2c54824fc7b05244838bb8fedeedb062033d65ac0825538eb"
  },
  {
    "path": "tests/test_search_providers.py",
    "size": 958,
    "sha256": "c48529f8fc25f00f9e63051def5889eeef9aa2bc572c1be2e31597ed5c1f773d"
  },
  {
    "path": "tests/test_fetch_messages_missing_db.py",
    "size": 718,
    "sha256": "0b5c375244c87eb2e67ca96544a9a03fe72423095fac680fca9b333435eed5cb"
  },
  {
    "path": "tests/test_accelerate_shim.py",
    "size": 2243,
    "sha256": "6557998ef84d08d98496d0b75df57590fe695537e55f68ea8e229f85c488a163"
  },
  {
    "path": "tests/test_ingestion_io.py",
    "size": 1948,
    "sha256": "ab78052bec99049a7f6dee5c6da731a5f9a80f4a197f1be52830898a60123145"
  },
  {
    "path": "tests/test_parse_when.py",
    "size": 511,
    "sha256": "f2fad510aeff80760e12254ea09c7218f7f20dbfe8e358fe1c61fdcb7f6138df"
  },
  {
    "path": "tests/test_metrics_tb.py",
    "size": 637,
    "sha256": "3f10c6b2d4ed6df5cd7bd8bf8b1194c2209bf482a35fb12c8c53027632e21b3d"
  },
  {
    "path": "tests/test_mlflow_step_logging.py",
    "size": 5868,
    "sha256": "a054b75a8d34559084e0a803cca1026d8f29de31455c20808ecb6e3079c29edb"
  },
  {
    "path": "tests/test_session_logger_wal.py",
    "size": 307,
    "sha256": "d253b6fab3dbc2a7fb9fd60022f9c0e5a3b2a24c95bb7e06e3d18a5d4db565bf"
  },
  {
    "path": "tests/test_metric_curves.py",
    "size": 346,
    "sha256": "8eba52b6b3bc6e7d06bc059455dae2071a8c3e8b6ac0884fad06d8905ba1b1b8"
  },
  {
    "path": "tests/test_safety.py",
    "size": 1160,
    "sha256": "e4140552917b7c579e8735ed1b3a7374eee34c85af73c0a9b82750552b963099"
  },
  {
    "path": "tests/test_tokenizer_roundtrip.py",
    "size": 782,
    "sha256": "739fd707efbeaa7561a54d474117b7db735296ba5702cdcddd86f42067dd57aa"
  },
  {
    "path": "tests/test_tokenizer_wrapper.py",
    "size": 802,
    "sha256": "957b6cde6caa641c72dee5725809dfc8fed67af7ace55b35a3dd8fb4a1662aa8"
  },
  {
    "path": "tests/test_sqlite_pool_close.py",
    "size": 1466,
    "sha256": "fb256e726e6b33f208a0f04face089b7be1ba00000f7bb0f90edb6737a3ae914"
  },
  {
    "path": "tests/test_ndjson_writer.py",
    "size": 437,
    "sha256": "06ee3933c93e89d43989a6b122feb57f628212392b04716fa9909a82ab9a03f2"
  },
  {
    "path": "tests/test_chat_session.py",
    "size": 2883,
    "sha256": "a34abb27699f0994a5107bb55714cd2b60aec8cfccfde64bc0f1c10dd23107d4"
  },
  {
    "path": "tests/test_checkpointing.py",
    "size": 551,
    "sha256": "b8d90b019a391afc5effa4789cf1d8ac3cf8327fbe0f6935370606338d31ec25"
  },
  {
    "path": "tests/test_checkpoint_manager.py",
    "size": 1495,
    "sha256": "de6ad25871c23c6f29c735ec3a65afb6151cd93c43e6d9a83fb0c0ac08cd3d11"
  },
  {
    "path": "tests/test_metrics.py",
    "size": 1254,
    "sha256": "8785850ea368faf5254bc0b4f8e43b355befbdbd9c0d9c952d43bdd5961deadb"
  },
  {
    "path": "tests/test_eval_runner.py",
    "size": 634,
    "sha256": "2a3e4480275264c4c8c5eed3b581c3cc07b3945c367efdb6f697df349e862b33"
  },
  {
    "path": "tests/test_trainloop_grad_accum.py",
    "size": 168,
    "sha256": "096235e9b830228b16f136a4fe9f679b85218fc94f813015ae8c0f5cf54c69f7"
  },
  {
    "path": "tests/test_hf_tokenizer_padding.py",
    "size": 974,
    "sha256": "b7f8f1d85ea9d65c754790d10134e8c0d902208984dacee6d3325e04decd4610"
  },
  {
    "path": "tests/test_tokenizer.py",
    "size": 551,
    "sha256": "c859296e39bedfdd03ea6ad91f2d364ea36370022fb649ace5ea3ef47a1b9555"
  },
  {
    "path": "tests/test_db_utils.py",
    "size": 1608,
    "sha256": "a6590e609f018a1847ca28d1988eeb3cab9edd2403113db5fddf0dc30aa6999b"
  },
  {
    "path": "tests/test_codex_run_tasks.py",
    "size": 4235,
    "sha256": "d7cb20103690e39eb34c2e8b048e647973e9ca47ae54f3f176ac1575092c1ba3"
  },
  {
    "path": "tests/test_ndjson_db_parity.py",
    "size": 1291,
    "sha256": "d61e07a7b3f6cd97dcf7a0f212218cf9896296fc6f834454d8120ab63b646249"
  },
  {
    "path": "tests/test_session_logger_log_adapters.py",
    "size": 1096,
    "sha256": "0c30ac338c7d657bf6a4c13961041d8f6e8f737ccbc4e4e869d2f6bc831d8ddd"
  },
  {
    "path": "tests/test_ingestion_encoding_coverage.py",
    "size": 2095,
    "sha256": "6e9c5b495f1292257149bc9f44fb6f3efd323703c105241200ebbc97cd08d015"
  },
  {
    "path": "tests/test_codex_maintenance.py",
    "size": 520,
    "sha256": "c4dfa078e33b72dd1297e5230d9a868a8e2c7eb84d41801e1855fc7679f39aa2"
  },
  {
    "path": "tests/test_monitoring_thread.py",
    "size": 830,
    "sha256": "3fdd6019a0518e4aea7ee8d69cbd6ef17dc9ffb3b27083710a5aee0a48995f6c"
  },
  {
    "path": "tests/test_repo_option_a.py",
    "size": 725,
    "sha256": "4b2fd6390fccab90c0b7e3c4efafdb2999b1598431e4eabd334bb23b36b99d56"
  },
  {
    "path": "tests/test_error_log.py",
    "size": 314,
    "sha256": "64beb5778b06304f29b5e393d6df7e9027ffa3929fdc340fa6cf0c6d97ab173b"
  },
  {
    "path": "tests/test_log_adapters.py",
    "size": 528,
    "sha256": "b0cd525635fb3daf87d6456493b63eb81613c7a169333eaced364c7fdcabe1bf"
  },
  {
    "path": "tests/test_env_logging.py",
    "size": 816,
    "sha256": "1dac5850a850c76601489bbbf1917aa0cc5d20c228ef5e55cb317567af727240"
  },
  {
    "path": "tests/test_checkpoint_system_meta.py",
    "size": 324,
    "sha256": "034f64f451013b5af0ae9c851c98589697119d3818e960b33fb7eb76b5d06ad6"
  },
  {
    "path": "tests/test_repro_determinism.py",
    "size": 642,
    "sha256": "92e841bb549d74c928209fef025c3655f2fb67f1cd90d605d50d407d80ecbe65"
  },
  {
    "path": "tests/test_peft_adapter.py",
    "size": 1043,
    "sha256": "d0455690f159a1f8d14440c26507c841fc352141150d6d51e9cf33d22a8f2265"
  },
  {
    "path": "tests/test_cli_train_engine.py",
    "size": 687,
    "sha256": "ea6760946fd852f5c6d55baf1d03b378350f16fd81024ce34fb96fbdc956d3d2"
  },
  {
    "path": "tests/test_chat_env_cleanup.py",
    "size": 504,
    "sha256": "a8581b5fefdf4512fa177531be5cf6f12a8c65ea38c58bbceb82801db43dc2c9"
  },
  {
    "path": "tests/test_symbolic_pipeline.py",
    "size": 4166,
    "sha256": "d9650656120c02eb5af4740b6913b3ca759a3d9f90c97a4e391ded36efc99fa4"
  },
  {
    "path": "tests/test_resume.py",
    "size": 2133,
    "sha256": "3713f64169ec59e5fe3b1924d290cbcf650a9fe8298c7f1bb8da71b84fb36df0"
  },
  {
    "path": "tests/test_mlflow_utils.py",
    "size": 8122,
    "sha256": "b6465b5debe036530a1624ef52d1a56d0835aeb8db32fb8c9acdd6223808b313"
  },
  {
    "path": "tests/test_pipeline.py",
    "size": 372,
    "sha256": "471e069fd07e893ad6f0c97c963289c9d0baeb777fbca0d15b8dae5004974485"
  },
  {
    "path": "tests/test_mlflow_utils_root.py",
    "size": 4331,
    "sha256": "f9dedbc92395a5e16e4d30153af70112a825dbdc96c3482b6e395b1fe815f2a2"
  },
  {
    "path": "tests/test_peft_integration.py",
    "size": 418,
    "sha256": "96350d13f3f67f007adfe217caf5848b79d8d8ce4b63f43d23d4a395abf44976"
  },
  {
    "path": "tests/conftest.py",
    "size": 2021,
    "sha256": "91cb096f177a6f1408265453d8d36f8f468ee5e3361cc847cd18fd4ce1ca43d6"
  },
  {
    "path": "tests/test_query_logs_build_query.py",
    "size": 17260,
    "sha256": "4dd210abd07cb8b2a513348db0de7865d7a6e325b263a32fadaf19806be8ad4f"
  },
  {
    "path": "tests/test_requirements_lock.py",
    "size": 515,
    "sha256": "5f59c18f41654b6cbc6565150d06eb026d76444fe6e75bada70359009594dc43"
  },
  {
    "path": "tests/test_import_ndjson_cli.py",
    "size": 1963,
    "sha256": "c9ec33358d4f6c81d4f6ab5a1e6db70d98de3e71a63ee9af90c21af997ec3fcd"
  },
  {
    "path": "tests/test_session_query_smoke.py",
    "size": 1405,
    "sha256": "aac513783b7759c220b11bfeba14ae6c3f182b3a1c37c8a1d1be095a559516be"
  },
  {
    "path": "tests/test_run_eval_cli.py",
    "size": 759,
    "sha256": "b8509a319b09b910f56f0055b4b9ef8b3007499f291ce3d624bdd14b5cef5a36"
  },
  {
    "path": "tests/test_tokenization.py",
    "size": 758,
    "sha256": "f52250a500b73464fc2445ecae99cc631bb3b322f5c4c352a61b4044ce1338a7"
  },
  {
    "path": "tests/test_data_utils.py",
    "size": 1151,
    "sha256": "7f97d779a085b63c4cdf041f63f21f821325f20f996dec8f364726d1e5ec7ff1"
  },
  {
    "path": "tests/test_nox_tests_delegation.py",
    "size": 721,
    "sha256": "cfa093e379b4fc51426fe7b4193a7dbc937cb3dea7023fd60201572fd964dbc8"
  },
  {
    "path": "tests/test_interfaces_hf_tokenizer.py",
    "size": 691,
    "sha256": "cca4b96e6fe66a07a1af414909d7a620dfbff7a5068e89ea5f275f5450b16b5a"
  },
  {
    "path": "tests/test_checkpoint_checksum.py",
    "size": 5491,
    "sha256": "331e174b2fcba69fbe8daac119c467cdf2e99927252be5de4cd9ae5457a1b296"
  },
  {
    "path": "tests/test_registry.py",
    "size": 628,
    "sha256": "8e569aaa4c17946300a7d62a9bd03381139df660ed73e3f50c10809aa3b22b84"
  },
  {
    "path": "tests/test_logging_viewer_cli.py",
    "size": 2067,
    "sha256": "b69f53ea6fba2335b057892e1fc0d7fc94986c1d71ea103eb1551e300205a805"
  },
  {
    "path": "tests/test_interfaces_compat.py",
    "size": 3413,
    "sha256": "239ad65a5c95aabed75937fca6cfa79b4ae0e84c9c051533898e31bb71d6aff7"
  },
  {
    "path": "tests/test_seeded_shuffle.py",
    "size": 257,
    "sha256": "7c7831167bdb9c3b5ea228db7af6da8919ddf56b238bbb20707baaa93cad28f3"
  },
  {
    "path": "tests/test_query_logs_tail.py",
    "size": 1286,
    "sha256": "3c94f20b13414131362a9091e05c405fb82199b42b5d67ca56191d73bb23701d"
  },
  {
    "path": "tests/test_import_ndjson_dedup.py",
    "size": 1365,
    "sha256": "ff8b5eac06c418b256bf8cd79216a972f9ec2131ccd99559e009f8baeaf9f8d6"
  },
  {
    "path": "tests/test_engine_hf_trainer.py",
    "size": 5377,
    "sha256": "d95eaf9c7180a2c05850a7afc3b88b589ad55e19ee5344e6d62fef5a0a6d2278"
  },
  {
    "path": "tests/test_dataset_manifest.py",
    "size": 325,
    "sha256": "11aa3ad7d8e0b87263f39d5470d3cfaf90be38910a040059af149a045619a712"
  },
  {
    "path": "tests/test_model_loader.py",
    "size": 8260,
    "sha256": "9a1826bc7bb9ddfe043ae6b80826095f16845896e06db98935e8a84fbed394e4"
  },
  {
    "path": "tests/test_export.py",
    "size": 1605,
    "sha256": "368800b9e495c12d1fef9e88a74f50d69be250d248188d7437eaa335b66c2ac0"
  },
  {
    "path": "tests/test_git_tag.py",
    "size": 5606,
    "sha256": "70eacb07701544406fd8436dac61c0898cea425fb00d36a0c6972c5685c58e1f"
  },
  {
    "path": "tests/test_cli_help.py",
    "size": 528,
    "sha256": "2b3fda5b59fa86539594cb6220def763145d5afefec06166f0b085e0f3d967e3"
  },
  {
    "path": "tests/test_split_indices.py",
    "size": 438,
    "sha256": "ebc796e78e580fd31e3e1275de2e6c3e7b2ad56d191c2fc13cc0321c71bfc220"
  },
  {
    "path": "tests/test_sqlite_pool.py",
    "size": 1266,
    "sha256": "20c3f4abf46a5754691812d8cecaf1c69c4b13a2959f39e85bd1261ef964d94b"
  },
  {
    "path": "tests/test_train_loop.py",
    "size": 7914,
    "sha256": "1831a30a3c7d3177c7aa25c48d093cca7689b63e9cb9fd48016230d4f7bb19ac"
  },
  {
    "path": "tests/test_tokenizer_ids.py",
    "size": 216,
    "sha256": "27a9736324d0fb8898ea35726622a668b121fc4c3c5d99b2a9e626952afd009b"
  },
  {
    "path": "tests/_codex_introspect.py",
    "size": 3892,
    "sha256": "41fa2cf8965d01d869c29eabe34a95e300a282f42056dc28a6313dca777e13c5"
  },
  {
    "path": "tests/test_cli.py",
    "size": 1761,
    "sha256": "5be584dcdbc56fb6ad2544fcb6b64aecd9659d8855a28538123fcce6b09019f1"
  },
  {
    "path": "tests/test_deep_research_task_process.py",
    "size": 1167,
    "sha256": "7d493175e3c89556052c2035ebdbc64be587a4ddb90a657bc708adf4bdc7fece"
  },
  {
    "path": "tests/test_api_rate_limit.py",
    "size": 374,
    "sha256": "46b7aef2def025b280e2caadaccc799391279b12f510436943746c0e6c572058"
  },
  {
    "path": "tests/test_ingestion_read_text.py",
    "size": 485,
    "sha256": "caee162bada625c5846faa259c465464455b0db446976335e045db1eedac53c2"
  },
  {
    "path": "tests/test_run_functional_training_tokenizer.py",
    "size": 803,
    "sha256": "e5bffc26643b5cc1c3e532356d959d19dc505c08321c0e9ca12922175d0c0dcc"
  },
  {
    "path": "tests/test_ingestion_family_encoding.py",
    "size": 1188,
    "sha256": "b59aa07d2ef4336985e4793a5db9b133291ccb2bc5c2b5c7c52d158a82527d14"
  },
  {
    "path": "tests/test_checkpoint_roundtrip.py",
    "size": 516,
    "sha256": "b2efb41dd8b733fcce69152639844616f243de52b819f836f46cd6012716096f"
  },
  {
    "path": "tests/test_static_code_analysis_step.py",
    "size": 531,
    "sha256": "fc6db617a2d077d01b9b1c1a24d668c33dcf4b2aaf3dd3c287d23b06ac4cb579"
  },
  {
    "path": "tests/__init__.py",
    "size": 31,
    "sha256": "9969f014c1eff35fdd278c7282adc4d62cb1a00c4c0c00077bcfc3176e2ebcb4"
  },
  {
    "path": "tests/test_training_callbacks.py",
    "size": 802,
    "sha256": "f33ce4102409022be77c4e12a69a05a6f5505a51ff26d19ea6a3fbc52c507889"
  },
  {
    "path": "tests/test_checkpointing_utils_extra.py",
    "size": 768,
    "sha256": "f2668db94582f3f6f0d315cde1f8b13a85daa0c7129fc7630b901d866dac7600"
  },
  {
    "path": "tests/test_minilm_forward.py",
    "size": 920,
    "sha256": "fd8fc667e96403d27ac41716374e933cb60a598693e861f0527f07970b35023a"
  },
  {
    "path": "tests/test_codexml_cli.py",
    "size": 1922,
    "sha256": "9d457b9978f852e9738efc840f3866f20c7b33df1f2279d9b5f1b0e1fca819e3"
  },
  {
    "path": "tests/test_determinism.py",
    "size": 230,
    "sha256": "4c5dfbd4ef736464a138b0e48d4704d59d06681920f3e2735bf5315cdf921b2f"
  },
  {
    "path": "tests/test_data_cache_sharding.py",
    "size": 297,
    "sha256": "d3b6e74386c1a798366c2b5c5521bd00ac94ae420293a2381b2df5e9899a8994"
  },
  {
    "path": "tests/test_cli_smoke.py",
    "size": 528,
    "sha256": "87a7748410a84e55476455eb9eb20d9774c58b1eea09a15551fad7e718ef77d6"
  },
  {
    "path": "tests/test_runner_doctor.py",
    "size": 517,
    "sha256": "c7de20210647f0edb3eb4b148cf7461cfa729bb1c7f0af7e436bf875e94ebc7c"
  },
  {
    "path": "tests/test_splits.py",
    "size": 454,
    "sha256": "8a194321a70e13144921901660037804c6339fff0b71085fa5bd246643baad80"
  },
  {
    "path": "tests/test_ingestion_split_cache.py",
    "size": 591,
    "sha256": "f9a58493cbb8cb18d149d8b683f26f70fbb364bdf3cf9c93bc60b13364a1b768"
  },
  {
    "path": "tests/test_session_logging.py",
    "size": 11290,
    "sha256": "e86b16d2ae6387a86fcbeaaeb19225a8d2412ec3e25b0faa237d3906e181b0c6"
  },
  {
    "path": "tests/test_session_logging_mirror.py",
    "size": 641,
    "sha256": "7740c619fcb9c8beedc5114d3fa13d526da9aa12d7057d64698daed4566b2a09"
  },
  {
    "path": "tests/test_db_utils_table_name.py",
    "size": 759,
    "sha256": "31d92f5da0236b5a1145e13d860814f038c5402d6775b6685d042970b34ab2da"
  },
  {
    "path": "tests/test_sentencepiece_adapter.py",
    "size": 15758,
    "sha256": "6e121a9fc25e988730fd915329f1ed8f2cc03a583f7beec6ba8dc485c177b7a8"
  },
  {
    "path": "tests/test_semparser.py",
    "size": 354,
    "sha256": "350a63fda89359e8040ef2fa08a3c2fb94a1b533d9eafaf7a7a287613d6cff6a"
  },
  {
    "path": "tests/test_hydra_cli.py",
    "size": 441,
    "sha256": "bb728127eb1480180ad4aab579992ef2e7af14705527837b55e2f39615b490af"
  },
  {
    "path": "tests/test_repro_helper.py",
    "size": 569,
    "sha256": "1012e3cc606736c99034c95262c2c4f299d6e08342801a9f7098b4a233710f97"
  },
  {
    "path": "tests/test_label_policy_lint.py",
    "size": 2341,
    "sha256": "401308f9e2d2bc4a2864c7cca2a98d9213b107eb1099639f2ac728b7741b73ec"
  },
  {
    "path": "tests/test_ingestion_seeded_shuffle.py",
    "size": 271,
    "sha256": "e3c9c89957aef6d23f187c7f6094775c3f1697a7092f62244f021b76abbdb4db"
  },
  {
    "path": "tests/test_repro_cli.py",
    "size": 1112,
    "sha256": "0f1d0ecac0f091b317a35a0c51c0c74f898c1ba6e1b109c37522d86ab8d6f6e3"
  },
  {
    "path": "tests/test_conversation_logger.py",
    "size": 700,
    "sha256": "68c1ff2c21c081efc8c6b380b1c4ad1b6c16e090b7b8ae759f3f652bcaf49592"
  },
  {
    "path": "tests/test_readme_examples.py",
    "size": 831,
    "sha256": "9caa4933b35eacc5613912865f7ad045e759bd9b70afced68c2f6eb5bf2a14ab"
  },
  {
    "path": "tests/test_deploy_codex_pipeline.py",
    "size": 3383,
    "sha256": "6eedf38eed224f3fa2e50a41b5791906185898c26a65971d3d22f445dba2ded0"
  },
  {
    "path": "tests/test_session_hooks.py",
    "size": 4978,
    "sha256": "6ae94d1ac3aa09202ff1cb48a0d5d939964779e6ae7de5d8b570b2e33394c6f2"
  },
  {
    "path": "tests/test_api_secret_filter.py",
    "size": 354,
    "sha256": "e00263a1dcf91066fe35d8d92d9ba45ce0c0663a526893e777ea99c3cff98538"
  },
  {
    "path": "tests/test_ndjson_logging.py",
    "size": 486,
    "sha256": "2d9185352950150496c9fd210c1331f78d974d4ce1b8ca686c8d09656ff77c20"
  },
  {
    "path": "tests/test_fetch_messages.py",
    "size": 5331,
    "sha256": "32b4bbbc7245a6582f1b48786c83d3a72a62141a10615b4a5604bed08e38f32f"
  },
  {
    "path": "tests/test_precommit_config_exists.py",
    "size": 214,
    "sha256": "6febaf9832f6203fa77f3e909030d3a922078008b3907d4a0ce2d1ca22071baf"
  },
  {
    "path": "tests/test_loaders.py",
    "size": 1488,
    "sha256": "6b0795700b75025451b670eed6ba07ca78169cf8601a99e158bb5d4d2f222adc"
  },
  {
    "path": "tests/test_ingestion_encodings_matrix.py",
    "size": 681,
    "sha256": "8bc1ead02534bf286bf836214448294e60a2c35c22107b1c1222198a376315a3"
  },
  {
    "path": "tests/test_telemetry_degrade.py",
    "size": 400,
    "sha256": "535ccb449eb804262218d752901496b3ad02962751cee068fe19cc10bc78efec"
  },
  {
    "path": "tests/test_repro_branches.py",
    "size": 582,
    "sha256": "23fbd9ab2fef979fd2ed872742c1efb04cb14f18a898af822c0aa27773e9ba13"
  },
  {
    "path": "tests/test_callbacks.py",
    "size": 3041,
    "sha256": "5703f01a096eaef236e942c01b41520e002a486f2aae719cbd20bad51566423a"
  },
  {
    "path": "tests/test_offline_repo_auditor.py",
    "size": 1115,
    "sha256": "ea83d928849f976c902fe60d64f979e2dd803ccda35dd9c15a59f057248d9aec"
  },
  {
    "path": "tests/test_session_hooks_warnings.py",
    "size": 793,
    "sha256": "db44da76b11b78751a59ffd6a0675657a4260b29c95d613363357761f57e38e7"
  },
  {
    "path": "tests/test_import_ndjson.py",
    "size": 2215,
    "sha256": "7cf40685d778466f9390f1a3f634e290d277ee88653ed9a0dc4790ffa224f252"
  },
  {
    "path": "tests/test_training_arguments_flags.py",
    "size": 354,
    "sha256": "35af57943aa7b988096f5590b2147bd1e23291482d5adbe087dd19d58a5a277b"
  },
  {
    "path": "tests/test_engine_hf_trainer_grad_accum.py",
    "size": 273,
    "sha256": "957e9198cf163583643d3a318ca5b8cd788b98ec04a5e14714c9a0f41072cb83"
  },
  {
    "path": "tests/test_utils_training_callbacks.py",
    "size": 613,
    "sha256": "fd6a2cd19f0071fce16d1683dee8ccf7c72d1353fbcd60aec1f4a07d6397f7f9"
  },
  {
    "path": "tests/test_chat_session_exit.py",
    "size": 1020,
    "sha256": "6bdbab6ad15ab6bfd684b0ba12b0a8648db17cf5e6a544fe14d7c97568c52519"
  },
  {
    "path": "tests/test_codex_cli.py",
    "size": 522,
    "sha256": "7c697df940df37df01f0eb047a712702f017a1236761b75a6838cb410d6d9370"
  },
  {
    "path": "tests/test_import_codex.py",
    "size": 72,
    "sha256": "ed7816909932a7e15fd62978ec0b7e81bd99f9950f85deae280eacffd70d1d65"
  },
  {
    "path": "tests/test_metrics_logging.py",
    "size": 772,
    "sha256": "ea49a90eb00cbb89dd110ebd8d20a6a73179588add8a89bd1c6948097092baf9"
  },
  {
    "path": "tests/test_activations.py",
    "size": 255,
    "sha256": "1eee1dfc827f6db02dfa2e2baa1a799a168bc6b8416b6cb177c505cdfbf1f9e8"
  },
  {
    "path": "tests/test_sqlite_wal.py",
    "size": 798,
    "sha256": "6a30afda5dd528dab55cbf4837f8400258213e86e4ec2f1e0885cc64874de4e4"
  },
  {
    "path": "tests/test_repo_option_b.py",
    "size": 474,
    "sha256": "49934f8bb91fdae574c219867bf9c9718fd6b6a7634151314068fc33808b5528"
  },
  {
    "path": "tests/test_sqlite_sanitize.py",
    "size": 347,
    "sha256": "a3b55aec819972202f6ce410282f0a61eb010fdbe4db2c147af9cba371c817e6"
  },
  {
    "path": "tests/test_modeling_utils.py",
    "size": 1398,
    "sha256": "f4d9ac60d3c9c98601c4837944f457814a9fd36a6c853e45f03381958b85ff8c"
  },
  {
    "path": "tests/test_ingestion_auto_encoding.py",
    "size": 576,
    "sha256": "344bca5deb72ac587dca8bd8d48138699ddf088ddedebedcb036530b09adf361"
  },
  {
    "path": "tests/test_tokenizer_batch_encode.py",
    "size": 6339,
    "sha256": "aeae67643918b61012a7a7d8ecca06ecc8048d1d4f8a3752e7f4e0cf2ff857ee"
  },
  {
    "path": "tests/data/test_cache_roundtrip.py",
    "size": 910,
    "sha256": "7e27bcb9fa80487af252cd0ce033ef845494970fdf3c2ad0ccc5fdcf8cf380f3"
  }
]
```

</details>

## Outstanding Codex Automation Questions

Canonical source: docs/status_update_outstanding_questions.md (update there first, then copy the refreshed table below).

| Timestamp(s) | Step / Phase | Recorded blocker | Status | Current disposition |
| --- | --- | --- | --- | --- |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | Hook execution failed because `yamllint`, `mdformat`, and `detect-secrets-hook` were missing. | Retired | The active pre-commit configuration only invokes local commands (ruff, black, mypy, pytest, git-secrets, license checker, etc.), so those CLIs are optional for developers and no longer required by automation. |
| 2025-08-28T03:55:32Z | PH6: Run pytest with coverage | `pytest` rejected legacy `--cov=src/codex_ml` arguments. | Retired | Coverage flags were removed from `pytest.ini`, and the nox helper now targets `src/codex`, so the legacy failure mode is obsolete. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | `check-merge-conflicts` and ruff flagged merge markers / unused imports. | Retired | The hook set no longer includes `check-merge-conflicts`; ruff/black remain for lint enforcement, so the merge-marker question is superseded. |
| 2025-09-10T05:02:28Z | `nox -s tests` | Coverage session failed during the gate. | Action required | `nox -s tests` still delegates to the coverage session, so the suite must pass with coverage enabled before this blocker can be closed. |
| 2025-09-10T05:45:43Z; 08:01:19Z; 08:01:50Z; 08:02:00Z | Phase 4: `file_integrity_audit compare` | Compare step reported unexpected file changes. | Resolved | Allowlist now covers the `.github/workflows.disabled/**` migration, validation manifests, and helper tooling; refreshed manifests (`.codex/validation/pre_manifest.json` ↔ `.codex/validation/post_manifest.json`) produce zero unexpected entries (`.codex/validation/file_integrity_compare.json`). |
| 2025-09-10T05:46:35Z; 08:02:12Z; 13:54:41Z | Phase 6: pre-commit | Hook execution failed because `pre-commit` was missing in the environment. | Action required | Install or gate `pre-commit` in the validation environment as documented; automation still expects it to be present. |
| 2025-09-10T05:46:47Z; 08:02:25Z; 13:55:11Z | Phase 6: pytest | Test suite failed under the gate. | Action required | Failures stem from missing optional dependencies and locale/encoding issues; install the extras or skip affected tests per the remediation notes. |
| 2025-09-10T05:46:52Z; 07:14:07Z; 08:02:32Z | Phase 6 & Validation: MkDocs | MkDocs build aborted (strict mode warnings / missing pages). | Mitigated / deferred | MkDocs now runs with `strict: false`, and navigation gaps were patched. Keep docs healthy before attempting to re-enable strict mode. |
| 2025-09-10T07:13:54Z; 11:12:28Z | Validation: pre-commit | `pre-commit` command not found during validation. | Action required | Same remediation as the Phase 6 failures—install or gate `pre-commit` before running validation jobs. |
| 2025-09-10T07:14:03Z; 11:12:36Z | Validation: pytest | Legacy `--cov=src/codex_ml` arguments rejected. | Retired | Covered by the coverage tooling update; remove the legacy flags and rely on the current nox/pytest configuration targeting `src/codex`. |
| 2025-09-10T08:01:17Z | Phase 4: `file_integrity_audit compare` | `file_integrity_audit.py` rejected argument order. | Documented resolution | The script expects `compare pre post --allow-*`; follow the documented invocation to avoid the error. |
| 2025-09-10 (timestamp `$ts`) | `tests_docs_links_audit` | Script crashed with `NameError: name 'root' is not defined`. | Action required | Add `root = Path('.')` (or similar) before using the variable the next time the audit script runs; the fix is recorded but not applied. |
| 2025-09-10T21:10:43Z | Validation: nox | `nox` command not found. | Action required | Install `nox` prior to running the validation gate, per the documented remediation. |

