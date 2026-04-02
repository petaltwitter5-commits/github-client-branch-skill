---
name: github-client-branch
description: Create and push a dedicated client customization branch in a GitHub repository from a company name, then return the branch URL. Use when the user wants to start per-client custom development, asks to create a customer-specific branch, or provides a company name plus a GitHub repository URL and expects a branch link as output.
---

# GitHub Client Branch

## Overview

Create a dedicated client customization branch from a company name, push it to the target GitHub repository, and return the final branch URL.

This skill is for the common workflow: user gives a **company name** and a **GitHub repository URL**, and expects a ready-to-use client branch such as `client/miaoxing-youpin` plus the direct GitHub branch page link.

## Workflow

### 1. Validate inputs

Require these two inputs:

- Company name
- GitHub repository URL

If either is missing, ask only for the missing field.

Accepted GitHub URL forms include:

- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `git@github.com:owner/repo.git`

### 2. Normalize the branch name

Run `scripts/make_branch_slug.py "<company-name>"` to generate a safe slug.

Default branch naming rule:

- Prefix with `client/`
- Use lowercase
- Replace spaces and separators with `-`
- Remove unsafe punctuation
- Transliterate common Chinese company names to pinyin when possible
- If transliteration is not available, fall back to a cleaned ASCII-like slug or a manually chosen short slug

Examples:

- `喵星优品宠物用品有限公司` → `client/miaoxing-youpin`
- `Acme Pet Supplies Co., Ltd.` → `client/acme-pet-supplies`

If the generated slug is ugly or ambiguous, prefer a short readable branch name over a mechanically exact one.

### 3. Prepare the repository

Clone the target repository if it is not already present locally.

Recommended local directory rule:

- Reuse an existing local clone if already available
- Otherwise clone into `tmp/<repo-name>` under the workspace

Detect the default branch from remote HEAD before branching.

### 4. Create or reuse the branch

Inside the repository:

1. Fetch remote refs
2. Checkout the default branch
3. Pull latest changes
4. Create `client/<slug>` if it does not exist locally
5. If it already exists locally, checkout it

If the remote branch already exists, set upstream and reuse it instead of failing.

### 5. Push the branch

Push with upstream tracking:

```bash
git push -u origin <branch>
```

If the repository uses a non-`origin` remote for the target GitHub repo, push to that actual remote.

### 6. Return only the useful result

Return:

- Branch name
- GitHub branch URL

Output format:

- Branch: `<branch-name>`
- URL: `<github-branch-url>`

Construct the URL as:

`https://github.com/<owner>/<repo>/tree/<branch-name-url-encoded>`

## Implementation notes

- Prefer deterministic shell steps over vague guidance.
- If `gh` is logged in and useful, it may be used, but plain `git` is sufficient for branch creation.
- Do not force a commit.
- Do not open a PR unless the user explicitly asks.
- If authentication fails, stop and report the exact failing step.

## Resources

### scripts/

Use `scripts/make_branch_slug.py` to convert company names into safe branch slug candidates.
