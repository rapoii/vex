---
name: supply-chain-review
description: Best practices for supply chain review (SBOM generation, lockfile integrity, package signing, SLSA).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: security
triggers:
  - "review supply chain"
  - "generate sbom"
  - "verify lockfile"
  - "supply-chain-review"
---

# Supply Chain Review

Securing the software supply chain by ensuring the integrity of dependencies, generating Software Bill of Materials (SBOMs), and following SLSA frameworks.

## When to Activate
- Task involves generating an SBOM for a release.
- Reviewing lockfile changes in a Pull Request.
- Configuring package signing and provenance in CI/CD.

## How It Works

### Lockfile Integrity
Lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`, `Cargo.lock`) contain cryptographic hashes of downloaded packages.

```json
// Example yarn.lock snippet showing integrity hash
"lodash@^4.17.21":
  version "4.17.21"
  resolved "https://registry.yarnpkg.com/lodash/-/lodash-4.17.21.tgz#679591c564c3bffaae8454cf0b3df370c3d6911c"
  integrity sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==
```
When reviewing a PR, look out for unexpected changes to the `resolved` URL or `integrity` hash for a package version that didn't change.

### SBOM Generation
Generate SBOMs to list all components, libraries, and their licenses. CycloneDX and SPDX are the common standards.

```bash
# Node.js using @cyclonedx/cyclonedx-npm
npx @cyclonedx/cyclonedx-npm --output-file bom.json

# Python using cyclonedx-bom
pip install cyclonedx-bom
cyclonedx-py environment --outfile bom.json

# Docker image using Syft
syft my-image:latest -o cyclonedx-json > bom.json
```

### SLSA (Supply chain Levels for Software Artifacts)
SLSA provides a framework for supply chain integrity. Implement provenance generation in GitHub Actions using sigstore.

```yaml
# .github/workflows/build.yml
jobs:
  build:
    outputs:
      hashes: ${{ steps.hash.outputs.hashes }}
    # ... build steps ...
    
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.4.0
    with:
      base64-subjects: "${{ needs.build.outputs.hashes }}"
```

### Package Signing
Use Sigstore/Cosign to sign and verify container images or binaries.

```bash
# Sign a container image
cosign sign --key cosign.key user/app:v1.0.0

# Verify an image
cosign verify --key cosign.pub user/app:v1.0.0
```

## Verification Steps
1. Verify CI pipelines use strict version pinning or rely entirely on lockfiles (`npm ci`, `poetry install --no-root`, `cargo build --locked`).
2. Generate an SBOM and manually verify that critical dependencies are listed.
3. Review changes to lockfiles in PRs to ensure malicious packages aren't silently introduced.

## Common Pitfalls
- **Typosquatting**: Installing `electorn` instead of `electron`. Always double-check package names.
- **Ignoring lockfile conflicts**: Resolving merge conflicts in lockfiles manually can accidentally downgrade dependencies or alter integrity hashes. Regenerate the lockfile instead.
- **Running install scripts blindly**: Many packages run `postinstall` scripts. In high-security environments, use `--ignore-scripts` for npm.

## Related Skills
- `dependency-audit`: For scanning the SBOM and lockfiles for vulnerabilities.
- `release-workflow`: Integrating SBOM generation into the release process.