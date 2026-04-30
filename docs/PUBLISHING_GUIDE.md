# Publishing BDD Studio on GitHub

This repository is prepared for GitHub publication.

## Option A: Publish with the GitHub CLI

Install and authenticate GitHub CLI:

```bash
brew install gh
gh auth login
```

Then run:

```bash
./scripts/publish_to_github.sh --repo bddstudio --public
```

The script will:

1. initialize Git if needed,
2. create the GitHub repository if it does not exist,
3. commit the source tree,
4. push to GitHub,
5. create tag `v0.8.0`,
6. create a GitHub Release,
7. attach a source ZIP.

## Option B: Publish to an Existing Remote

Create an empty GitHub repository in the browser, then run:

```bash
./scripts/publish_to_github.sh --remote https://github.com/YOUR_USERNAME/bddstudio.git
```

## Option C: Manual Git

```bash
git init
git add .
git commit -m "Initial release of BDD Studio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bddstudio.git
git push -u origin main
```

## Student Install Link

After publishing, students can install with:

```bash
git clone https://github.com/YOUR_USERNAME/bddstudio.git
cd bddstudio
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
bddstudio serve
```
