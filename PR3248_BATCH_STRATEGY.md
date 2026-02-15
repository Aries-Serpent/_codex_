# PR #3248 Batched Collection Strategy

> **Agent Token Limit**: 30,000 tokens maximum  
> **Total Commits**: 81  
> **Strategy**: Batch processing in groups of 10-15 commits

---

## Batch Execution Plan

### Batch Configuration

```python
TOTAL_COMMITS = 81
BATCH_SIZE = 15  # Process 15 commits per agent call
TOTAL_BATCHES = 6  # 81 / 15 = 5.4, rounded up to 6
```

### Batch Definitions

**Batch 1** (Commits 1-15):
```
dd7b63779e9c7a2da8806a5b902778973eaf42bf, ec3d17b6eab2fdc170b7196429d643304ed12f4d,
d9731c9c5af4d31dbad2f0bf66220d20c19d04d4, 2a7e546fc698aba6a6131ed232a8b8e544211e4e,
0d96f686543854a0647cba99e81aacbcc17524b5, c36c47f24c70ca3912f11ecde51bb1552b6ebed5,
2378dc6a96df8465dbc8a4972b4fe8b6817ba2cc, a59dffd35d0875574db2fc806a687d84d6d8b99a,
483be0dea87f9b9097ef9c0d91a6efb36abc087b, 7267398869bcb253981fd10b300b0d6865825141,
9cc97df9e37aaef873b3271a0acee92f48af8234, 43d7f59bc2e4a26b635633e29dc6d6c0da2379e4,
77e29f0023896057bf406e2a59f382fbf3c80ccd, 701e1ca36718b69f4b5d990558c06e58bb389aa6,
1d5fccd38c5c9d7ba0c29e3435add0a754853102
```

**Batch 2** (Commits 16-30):
```
78c75ca6e435b4dfdc38ea1bd6f8237f25d6525a, 6593115b8e8ab13063fc0a48dded8a30fab1d755,
209ea2c216e4b1eb3b1b2c06bad541b6303071b0, f5212c6f651bece0657d182147ef4992f98f5891,
27212d4a493f2504878302a5315dcea0d853005c, 195947d6b23b739770b05fc24e228d872b2f1ed6,
e1a9a7cfbc50280bdfbf4f820b039c6237b37652, c643d565ce8a2f375d82805ed48f80900fc93c85,
0d8be400d4f7a045efa70ffd91cc3d72c1416960, 3a73d44792ce22f4ee2619336b00fb53707b650c,
5ca9ec6d9dfbd81e537315eb7954ca1cc943d17d, a77242d5cccd607731857f1f215a6abc5d4074a5,
2937fe5861bfa5e654c5c58c149895fea98095de, 89a32c56aec18457ee286ab9d27c9440c94e44a6,
ff937ef0f925d563d5b09ede40f22feb0b78f747
```

**Batch 3** (Commits 31-45):
```
6762050e4fbf7209097e188e859930027be3a072, 7666a701f0ce4715cbe2eedd5950a53e900a7ec1,
a37117c697b028c2bbc13f5f0519763acc3b7167, ce6917ac948ae6c432952a4a0df7ad0e33788d07,
5b44dd5d8d78b9e07858f10aabbccfdd08eb3ffe, 27daa3272aa9b13cd13c298a9fbd0392ccc39bf9,
a80e33fbe77a7f756d0e91bda7289b4385e7b26e, 43428572c5a75d8688a92ea61d4cdf00e6ab7d37,
721be8fbe6d1db02f1727a0189f1a6dd12d04c49, 0db24b5fb6fdf5e789b48f5c9cefa0632c09e48f,
3ab4364be487a92c9b38469bb3bcdb2efb2d8401, c57b5da02554aad84cd445e974679aff6625564e,
9ad5bc92bf7afac9d87836937dafc647a4d1df07, 9b194adb18bae4c8230930151ee2ceb178e1afa3,
dee711cde2e767ea8815fcc11bfa53bef84a84f7
```

**Batch 4** (Commits 46-60):
```
faf0ac3ed93c5930f26e06c79921ccae6f28a934, 07bf832d6ce42191797282f6f7d75f0810623e43,
4985bf797565b7e44421c70984299cbc42188b4c, 0640f7d1bd8f690ade3b5332efa2ed6822aab451,
c18eafd9a2941f491d5c903427894273e055ada0, 7f0379dfac8e4ccdfc386fb898b9ed1192aca83a,
28106e64c63a38aa70b39df39d8edf1bcdeafb35, 38c64fa215fd81714acf881aa9d0a6f1269445ef,
07713e4bfceb88294e1c7b674c0c47f69ca4fb8e, c067b49b388e4eb6f72edf5e035907c237c68338,
9a83b8c6c2ca64d95bed272ed9793e5dae4bdd4b, f58b5c1d93f9abf4bf8df033a346a68a817414a5,
f2ef77258695f77985cdf2071d7b3f4b1f22ee29, c3c07d1c032d02ef42250cf960d187164fe79bf2,
d088994633604a2bb8ba972d4d0ff7bf28a34fc7
```

**Batch 5** (Commits 61-75):
```
b3dbe1081be9c95f9e31446f4c0c20dea394500d, f45e5cca3cd62dc799eaa12ad01adc326962e736,
9db17bd601cbf4b4ddd536f432f961c543f1b6a5, 0442dabdfe87d4f60739d7f9208ea6cb6a408961,
1aae5439725fc713196003e306e314382852dcd6, 923a49a1abffd38b34a2de7d46c30129d847e78b,
87919506d93c5be061a7f5ea3591ef1dc587cf79, 7abdafa3fb1e510a3175f823c2cd93e2a556c9be,
01f06a53595becdc99aa556b411420d5aa8a9913, 066151aed9c435463afa995ee80451bec0541428,
44439905ea036b825ae3fc810049acb52547d87a, 0a2f6d4c98e4ad9264560b0f61564785451a91fa,
eec20cdd4b09d4d8254b8d48888180ba0566da4c, 2d1cdd2994374fa512cfac2afa2036b4f6fea8fb,
bb5f48f3b605a75b35a4a56de8555d9815f78fa2
```

**Batch 6** (Commits 76-81):
```
5312bbc45ddd4e7a42940c0fa4fdb61782ffaef7, 23a340db9b72e8f104df8623cc8e89ef26383d57,
480e70d70394016586e70db7491d95ad052e665c, ebed65dd3904d1f54d9f11e60a0a2474252177f0,
b3b90e185628a7831173d817396edc6e311c1574, aa3210e3074eae3ea98f4aa9d9e2e127d0a82d5a
```

---

## Execution Strategy

### Phase 1: Sequential Batch Processing

Execute batches sequentially to stay under token limit:

```bash
# Batch 1
@copilot Use ci-log-retrieval-agent to collect workflow runs and artifacts for commits:
dd7b637, ec3d17b, d9731c9, 2a7e546, 0d96f68, c36c47f, 2378dc6, a59dffd, 483be0d, 7267398, 9cc97df, 43d7f59, 77e29f0, 701e1ca, 1d5fccd

# Batch 2
@copilot Use ci-log-retrieval-agent to collect workflow runs and artifacts for commits:
78c75ca, 6593115, 209ea2c, f5212c6, 27212d4, 195947d, e1a9a7c, c643d56, 0d8be40, 3a73d44, 5ca9ec6, a77242d, 2937fe5, 89a32c5, ff937ef

# ... continue for all 6 batches
```

### Phase 2: Merge Results

After all batches complete, merge the partial results:

```python
# scripts/merge_pr3248_batches.py
import json
from pathlib import Path

batch_files = [
    "pr3248_batch1_data.json",
    "pr3248_batch2_data.json",
    "pr3248_batch3_data.json",
    "pr3248_batch4_data.json",
    "pr3248_batch5_data.json",
    "pr3248_batch6_data.json",
]

merged_data = {
    "pr_number": 3248,
    "repository": "Aries-Serpent/_codex_",
    "total_batches": 6,
    "commits": []
}

for batch_file in batch_files:
    if Path(batch_file).exists():
        with open(batch_file) as f:
            batch_data = json.load(f)
            merged_data["commits"].extend(batch_data.get("commits", []))

# Write merged output
with open("pr3248_complete_merged_data.json", "w") as f:
    json.dump(merged_data, f, indent=2)

print(f"✅ Merged {len(merged_data['commits'])} commits")
```

### Phase 3: Generate Final Outputs

```python
# Use merged data to populate failing_checks.md
python scripts/generate_failing_checks_table.py \
  --input pr3248_complete_merged_data.json \
  --output failing_checks.md
```

---

## Concise Agent Prompts

### Template for Each Batch

```
Collect CI data for these commits in PR #3248 (Aries-Serpent/_codex_):

Commits: [batch_commits_short_shas]

For each commit:
1. Find workflow runs (head_sha match)
2. Get jobs and artifacts for each run
3. Identify failures (conclusion: failure/timed_out/cancelled)

Output: pr3248_batch{N}_data.json with structure:
{
  "batch": N,
  "commits": [
    {
      "sha": "...",
      "runs": [{id, name, conclusion, html_url, jobs: [], artifacts: []}]
    }
  ]
}

Token estimate: ~5K per batch
```

### Estimated Token Usage

- **Per Commit**: ~200 tokens (SHA + metadata)
- **Per Workflow Run**: ~300 tokens (run + jobs + artifacts)
- **Per Batch (15 commits)**: ~5,000 tokens
- **Safety Margin**: ~10,000 tokens for agent overhead
- **Total per batch**: ~15,000 tokens (well under 30K limit)

---

## Progress Tracking

### Batch Status Table

| Batch | Commits | Status | Output File | Verified |
|-------|---------|--------|-------------|----------|
| 1 | 1-15 | ⏳ Pending | pr3248_batch1_data.json | ❌ |
| 2 | 16-30 | ⏳ Pending | pr3248_batch2_data.json | ❌ |
| 3 | 31-45 | ⏳ Pending | pr3248_batch3_data.json | ❌ |
| 4 | 46-60 | ⏳ Pending | pr3248_batch4_data.json | ❌ |
| 5 | 61-75 | ⏳ Pending | pr3248_batch5_data.json | ❌ |
| 6 | 76-81 | ⏳ Pending | pr3248_batch6_data.json | ❌ |

Update this table as batches complete.

---

## Alternative: Direct Agent Execution

Since I'm currently in the main agent context with full tools, I can execute this directly rather than delegating to a custom agent. Let me do that now.

**Decision**: Execute collection directly in current session using GitHub MCP tools.

---

## Immediate Next Steps

1. ✅ Create batch strategy document (this file)
2. ⏳ Execute direct collection using MCP tools in current session
3. ⏳ Generate merged output
4. ⏳ Update failing_checks.md
5. ⏳ Verify all 81 commits present
6. ⏳ Commit and push results

**Time Estimate**: 15-20 minutes for complete collection
