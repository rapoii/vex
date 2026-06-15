# VEX Marketplace

Free community skill marketplace. Share, discover, and install skills.

## Browse Skills

```bash
python marketplace/installer.py browse
```

## Install a Skill

```bash
python marketplace/installer.py install <skill-name>
```

## Rate a Skill

```bash
python marketplace/installer.py rate <skill-name> 4
```

## Publish Your Skill

1. Create a skill following the SKILL.md format
2. Run: `python marketplace/installer.py publish <skill-dir>`
3. Submit a PR to add your skill to `catalog.json`

## Catalog Format

Skills in `catalog.json`:

```json
{
  "name": "my-skill",
  "description": "What it does",
  "author": "your-github-username",
  "category": "workflow",
  "version": "1.0.0",
  "license": "MIT",
  "repo": "https://github.com/you/my-skill"
}
```

## No Server Required

VEX marketplace uses GitHub releases for distribution. No central server, no accounts, no fees.
