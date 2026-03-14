# [Investigation Request]: Failing Checks per Commit
> Generated: 2026-03-14 03:39:39 UTC
> Pull Request: #3248
> Repository: Aries-Serpent/_codex_
> HEAD SHA: 95bcc8abc008d588e86e8283e2eba669dee556cf

## ⚠️ Collection Status

**API Access Issue Detected:** All API calls returned `403 Forbidden`.

**Possible Causes:**
- DNS monitoring proxy blocking `api.github.com`
- GITHUB_TOKEN missing required scopes (`repo`, `actions:read`, `checks:read`)
- Rate limiting or authentication issues

**Required Actions:**
1. Verify token has `repo` + `actions:read` + `checks:read` scopes
2. Check network/proxy configuration
3. Consider alternative data collection methods (see below)

## Summary

This report is a **template** for 81 commits in PR #3248.
Actual check run and artifact data requires API access resolution.

## Template Table Structure

| Commit SHA | Failing Check Workflows (explicit links to failing runs) | Artifacts (download links) |
|---|---|---|
| [dd7b637](https://github.com/Aries-Serpent/_codex_/commit/dd7b63779e9c7a2da8806a5b902778973eaf42bf) | ⚠️ Pending API access | ⚠️ Pending API access |
| [ec3d17b](https://github.com/Aries-Serpent/_codex_/commit/ec3d17b6eab2fdc170b7196429d643304ed12f4d) | ⚠️ Pending API access | ⚠️ Pending API access |
| [d9731c9](https://github.com/Aries-Serpent/_codex_/commit/d9731c9c5af4d31dbad2f0bf66220d20c19d04d4) | ⚠️ Pending API access | ⚠️ Pending API access |
| [2a7e546](https://github.com/Aries-Serpent/_codex_/commit/2a7e546fc698aba6a6131ed232a8b8e544211e4e) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0d96f68](https://github.com/Aries-Serpent/_codex_/commit/0d96f686543854a0647cba99e81aacbcc17524b5) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c36c47f](https://github.com/Aries-Serpent/_codex_/commit/c36c47f24c70ca3912f11ecde51bb1552b6ebed5) | ⚠️ Pending API access | ⚠️ Pending API access |
| [2378dc6](https://github.com/Aries-Serpent/_codex_/commit/2378dc6a96df8465dbc8a4972b4fe8b6817ba2cc) | ⚠️ Pending API access | ⚠️ Pending API access |
| [a59dffd](https://github.com/Aries-Serpent/_codex_/commit/a59dffd35d0875574db2fc806a687d84d6d8b99a) | ⚠️ Pending API access | ⚠️ Pending API access |
| [483be0d](https://github.com/Aries-Serpent/_codex_/commit/483be0dea87f9b9097ef9c0d91a6efb36abc087b) | ⚠️ Pending API access | ⚠️ Pending API access |
| [7267398](https://github.com/Aries-Serpent/_codex_/commit/7267398869bcb253981fd10b300b0d6865825141) | ⚠️ Pending API access | ⚠️ Pending API access |
| [9cc97df](https://github.com/Aries-Serpent/_codex_/commit/9cc97df9e37aaef873b3271a0acee92f48af8234) | ⚠️ Pending API access | ⚠️ Pending API access |
| [43d7f59](https://github.com/Aries-Serpent/_codex_/commit/43d7f59bc2e4a26b635633e29dc6d6c0da2379e4) | ⚠️ Pending API access | ⚠️ Pending API access |
| [77e29f0](https://github.com/Aries-Serpent/_codex_/commit/77e29f0023896057bf406e2a59f382fbf3c80ccd) | ⚠️ Pending API access | ⚠️ Pending API access |
| [701e1ca](https://github.com/Aries-Serpent/_codex_/commit/701e1ca36718b69f4b5d990558c06e58bb389aa6) | ⚠️ Pending API access | ⚠️ Pending API access |
| [1d5fccd](https://github.com/Aries-Serpent/_codex_/commit/1d5fccd38c5c9d7ba0c29e3435add0a754853102) | ⚠️ Pending API access | ⚠️ Pending API access |
| [78c75ca](https://github.com/Aries-Serpent/_codex_/commit/78c75ca6e435b4dfdc38ea1bd6f8237f25d6525a) | ⚠️ Pending API access | ⚠️ Pending API access |
| [6593115](https://github.com/Aries-Serpent/_codex_/commit/6593115b8e8ab13063fc0a48dded8a30fab1d755) | ⚠️ Pending API access | ⚠️ Pending API access |
| [209ea2c](https://github.com/Aries-Serpent/_codex_/commit/209ea2c216e4b1eb3b1b2c06bad541b6303071b0) | ⚠️ Pending API access | ⚠️ Pending API access |
| [f5212c6](https://github.com/Aries-Serpent/_codex_/commit/f5212c6f651bece0657d182147ef4992f98f5891) | ⚠️ Pending API access | ⚠️ Pending API access |
| [27212d4](https://github.com/Aries-Serpent/_codex_/commit/27212d4a493f2504878302a5315dcea0d853005c) | ⚠️ Pending API access | ⚠️ Pending API access |
| [195947d](https://github.com/Aries-Serpent/_codex_/commit/195947d6b23b739770b05fc24e228d872b2f1ed6) | ⚠️ Pending API access | ⚠️ Pending API access |
| [e1a9a7c](https://github.com/Aries-Serpent/_codex_/commit/e1a9a7cfbc50280bdfbf4f820b039c6237b37652) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c643d56](https://github.com/Aries-Serpent/_codex_/commit/c643d565ce8a2f375d82805ed48f80900fc93c85) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0d8be40](https://github.com/Aries-Serpent/_codex_/commit/0d8be400d4f7a045efa70ffd91cc3d72c1416960) | ⚠️ Pending API access | ⚠️ Pending API access |
| [3a73d44](https://github.com/Aries-Serpent/_codex_/commit/3a73d44792ce22f4ee2619336b00fb53707b650c) | ⚠️ Pending API access | ⚠️ Pending API access |
| [5ca9ec6](https://github.com/Aries-Serpent/_codex_/commit/5ca9ec6d9dfbd81e537315eb7954ca1cc943d17d) | ⚠️ Pending API access | ⚠️ Pending API access |
| [a77242d](https://github.com/Aries-Serpent/_codex_/commit/a77242d5cccd607731857f1f215a6abc5d4074a5) | ⚠️ Pending API access | ⚠️ Pending API access |
| [2937fe5](https://github.com/Aries-Serpent/_codex_/commit/2937fe5861bfa5e654c5c58c149895fea98095de) | ⚠️ Pending API access | ⚠️ Pending API access |
| [89a32c5](https://github.com/Aries-Serpent/_codex_/commit/89a32c56aec18457ee286ab9d27c9440c94e44a6) | ⚠️ Pending API access | ⚠️ Pending API access |
| [ff937ef](https://github.com/Aries-Serpent/_codex_/commit/ff937ef0f925d563d5b09ede40f22feb0b78f747) | ⚠️ Pending API access | ⚠️ Pending API access |
| [6762050](https://github.com/Aries-Serpent/_codex_/commit/6762050e4fbf7209097e188e859930027be3a072) | ⚠️ Pending API access | ⚠️ Pending API access |
| [7666a70](https://github.com/Aries-Serpent/_codex_/commit/7666a701f0ce4715cbe2eedd5950a53e900a7ec1) | ⚠️ Pending API access | ⚠️ Pending API access |
| [a37117c](https://github.com/Aries-Serpent/_codex_/commit/a37117c697b028c2bbc13f5f0519763acc3b7167) | ⚠️ Pending API access | ⚠️ Pending API access |
| [ce6917a](https://github.com/Aries-Serpent/_codex_/commit/ce6917ac948ae6c432952a4a0df7ad0e33788d07) | ⚠️ Pending API access | ⚠️ Pending API access |
| [5b44dd5](https://github.com/Aries-Serpent/_codex_/commit/5b44dd5d8d78b9e07858f10aabbccfdd08eb3ffe) | ⚠️ Pending API access | ⚠️ Pending API access |
| [27daa32](https://github.com/Aries-Serpent/_codex_/commit/27daa3272aa9b13cd13c298a9fbd0392ccc39bf9) | ⚠️ Pending API access | ⚠️ Pending API access |
| [a80e33f](https://github.com/Aries-Serpent/_codex_/commit/a80e33fbe77a7f756d0e91bda7289b4385e7b26e) | ⚠️ Pending API access | ⚠️ Pending API access |
| [4342857](https://github.com/Aries-Serpent/_codex_/commit/43428572c5a75d8688a92ea61d4cdf00e6ab7d37) | ⚠️ Pending API access | ⚠️ Pending API access |
| [721be8f](https://github.com/Aries-Serpent/_codex_/commit/721be8fbe6d1db02f1727a0189f1a6dd12d04c49) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0db24b5](https://github.com/Aries-Serpent/_codex_/commit/0db24b5fb6fdf5e789b48f5c9cefa0632c09e48f) | ⚠️ Pending API access | ⚠️ Pending API access |
| [3ab4364](https://github.com/Aries-Serpent/_codex_/commit/3ab4364be487a92c9b38469bb3bcdb2efb2d8401) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c57b5da](https://github.com/Aries-Serpent/_codex_/commit/c57b5da02554aad84cd445e974679aff6625564e) | ⚠️ Pending API access | ⚠️ Pending API access |
| [9ad5bc9](https://github.com/Aries-Serpent/_codex_/commit/9ad5bc92bf7afac9d87836937dafc647a4d1df07) | ⚠️ Pending API access | ⚠️ Pending API access |
| [9b194ad](https://github.com/Aries-Serpent/_codex_/commit/9b194adb18bae4c8230930151ee2ceb178e1afa3) | ⚠️ Pending API access | ⚠️ Pending API access |
| [dee711c](https://github.com/Aries-Serpent/_codex_/commit/dee711cde2e767ea8815fcc11bfa53bef84a84f7) | ⚠️ Pending API access | ⚠️ Pending API access |
| [faf0ac3](https://github.com/Aries-Serpent/_codex_/commit/faf0ac3ed93c5930f26e06c79921ccae6f28a934) | ⚠️ Pending API access | ⚠️ Pending API access |
| [07bf832](https://github.com/Aries-Serpent/_codex_/commit/07bf832d6ce42191797282f6f7d75f0810623e43) | ⚠️ Pending API access | ⚠️ Pending API access |
| [4985bf7](https://github.com/Aries-Serpent/_codex_/commit/4985bf797565b7e44421c70984299cbc42188b4c) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0640f7d](https://github.com/Aries-Serpent/_codex_/commit/0640f7d1bd8f690ade3b5332efa2ed6822aab451) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c18eafd](https://github.com/Aries-Serpent/_codex_/commit/c18eafd9a2941f491d5c903427894273e055ada0) | ⚠️ Pending API access | ⚠️ Pending API access |
| [7f0379d](https://github.com/Aries-Serpent/_codex_/commit/7f0379dfac8e4ccdfc386fb898b9ed1192aca83a) | ⚠️ Pending API access | ⚠️ Pending API access |
| [28106e6](https://github.com/Aries-Serpent/_codex_/commit/28106e64c63a38aa70b39df39d8edf1bcdeafb35) | ⚠️ Pending API access | ⚠️ Pending API access |
| [38c64fa](https://github.com/Aries-Serpent/_codex_/commit/38c64fa215fd81714acf881aa9d0a6f1269445ef) | ⚠️ Pending API access | ⚠️ Pending API access |
| [07713e4](https://github.com/Aries-Serpent/_codex_/commit/07713e4bfceb88294e1c7b674c0c47f69ca4fb8e) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c067b49](https://github.com/Aries-Serpent/_codex_/commit/c067b49b388e4eb6f72edf5e035907c237c68338) | ⚠️ Pending API access | ⚠️ Pending API access |
| [9a83b8c](https://github.com/Aries-Serpent/_codex_/commit/9a83b8c6c2ca64d95bed272ed9793e5dae4bdd4b) | ⚠️ Pending API access | ⚠️ Pending API access |
| [f58b5c1](https://github.com/Aries-Serpent/_codex_/commit/f58b5c1d93f9abf4bf8df033a346a68a817414a5) | ⚠️ Pending API access | ⚠️ Pending API access |
| [f2ef772](https://github.com/Aries-Serpent/_codex_/commit/f2ef77258695f77985cdf2071d7b3f4b1f22ee29) | ⚠️ Pending API access | ⚠️ Pending API access |
| [c3c07d1](https://github.com/Aries-Serpent/_codex_/commit/c3c07d1c032d02ef42250cf960d187164fe79bf2) | ⚠️ Pending API access | ⚠️ Pending API access |
| [d088994](https://github.com/Aries-Serpent/_codex_/commit/d088994633604a2bb8ba972d4d0ff7bf28a34fc7) | ⚠️ Pending API access | ⚠️ Pending API access |
| [b3dbe10](https://github.com/Aries-Serpent/_codex_/commit/b3dbe1081be9c95f9e31446f4c0c20dea394500d) | ⚠️ Pending API access | ⚠️ Pending API access |
| [f45e5cc](https://github.com/Aries-Serpent/_codex_/commit/f45e5cca3cd62dc799eaa12ad01adc326962e736) | ⚠️ Pending API access | ⚠️ Pending API access |
| [9db17bd](https://github.com/Aries-Serpent/_codex_/commit/9db17bd601cbf4b4ddd536f432f961c543f1b6a5) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0442dab](https://github.com/Aries-Serpent/_codex_/commit/0442dabdfe87d4f60739d7f9208ea6cb6a408961) | ⚠️ Pending API access | ⚠️ Pending API access |
| [1aae543](https://github.com/Aries-Serpent/_codex_/commit/1aae5439725fc713196003e306e314382852dcd6) | ⚠️ Pending API access | ⚠️ Pending API access |
| [923a49a](https://github.com/Aries-Serpent/_codex_/commit/923a49a1abffd38b34a2de7d46c30129d847e78b) | ⚠️ Pending API access | ⚠️ Pending API access |
| [8791950](https://github.com/Aries-Serpent/_codex_/commit/87919506d93c5be061a7f5ea3591ef1dc587cf79) | ⚠️ Pending API access | ⚠️ Pending API access |
| [7abdafa](https://github.com/Aries-Serpent/_codex_/commit/7abdafa3fb1e510a3175f823c2cd93e2a556c9be) | ⚠️ Pending API access | ⚠️ Pending API access |
| [01f06a5](https://github.com/Aries-Serpent/_codex_/commit/01f06a53595becdc99aa556b411420d5aa8a9913) | ⚠️ Pending API access | ⚠️ Pending API access |
| [066151a](https://github.com/Aries-Serpent/_codex_/commit/066151aed9c435463afa995ee80451bec0541428) | ⚠️ Pending API access | ⚠️ Pending API access |
| [4443990](https://github.com/Aries-Serpent/_codex_/commit/44439905ea036b825ae3fc810049acb52547d87a) | ⚠️ Pending API access | ⚠️ Pending API access |
| [0a2f6d4](https://github.com/Aries-Serpent/_codex_/commit/0a2f6d4c98e4ad9264560b0f61564785451a91fa) | ⚠️ Pending API access | ⚠️ Pending API access |
| [eec20cd](https://github.com/Aries-Serpent/_codex_/commit/eec20cdd4b09d4d8254b8d48888180ba0566da4c) | ⚠️ Pending API access | ⚠️ Pending API access |
| [2d1cdd2](https://github.com/Aries-Serpent/_codex_/commit/2d1cdd2994374fa512cfac2afa2036b4f6fea8fb) | ⚠️ Pending API access | ⚠️ Pending API access |
| [bb5f48f](https://github.com/Aries-Serpent/_codex_/commit/bb5f48f3b605a75b35a4a56de8555d9815f78fa2) | ⚠️ Pending API access | ⚠️ Pending API access |
| [5312bbc](https://github.com/Aries-Serpent/_codex_/commit/5312bbc45ddd4e7a42940c0fa4fdb61782ffaef7) | ⚠️ Pending API access | ⚠️ Pending API access |
| [23a340d](https://github.com/Aries-Serpent/_codex_/commit/23a340db9b72e8f104df8623cc8e89ef26383d57) | ⚠️ Pending API access | ⚠️ Pending API access |
| [480e70d](https://github.com/Aries-Serpent/_codex_/commit/480e70d70394016586e70db7491d95ad052e665c) | ⚠️ Pending API access | ⚠️ Pending API access |
| [ebed65d](https://github.com/Aries-Serpent/_codex_/commit/ebed65dd3904d1f54d9f11e60a0a2474252177f0) | ⚠️ Pending API access | ⚠️ Pending API access |
| [b3b90e1](https://github.com/Aries-Serpent/_codex_/commit/b3b90e185628a7831173d817396edc6e311c1574) | ⚠️ Pending API access | ⚠️ Pending API access |
| [aa3210e](https://github.com/Aries-Serpent/_codex_/commit/aa3210e3074eae3ea98f4aa9d9e2e127d0a82d5a) | ⚠️ Pending API access | ⚠️ Pending API access |

---

## Alternative Collection Methods

### Method 1: GitHub CLI with Authenticated Session
```bash
# For each commit SHA
gh api /repos/Aries-Serpent/_codex_/commits/{SHA}/check-runs
gh api /repos/Aries-Serpent/_codex_/actions/runs?head_sha={SHA}
```

### Method 2: Playwright Browser Automation
Navigate to workflow run pages and scrape artifact links:
- https://github.com/Aries-Serpent/_codex_/actions/runs/{RUN_ID}

### Method 3: Manual UI Collection
Visit PR directly: https://github.com/Aries-Serpent/_codex_/pull/3248
- Check 'Checks' tab for failing workflows
- Click each workflow run to view artifacts

---

**Generated by:** `scripts/pr3248_mcp_collection_helper.py`
**Last Updated:** 2026-03-14 03:39:39 UTC
**Status:** Template generated - requires API access for actual data