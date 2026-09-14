# Samruddhi192105 Profile README

This package is a customized implementation of the profile-README system described in the supplied guide. The guide's key setup is a public repository whose name exactly matches the GitHub username. fileciteturn0file0L64-L82

## Create the repository

Create a **public** GitHub repository named:

`Samruddhi192105`

## Install the local dependency

```powershell
pip install pillow
```

The guide uses Pillow for its portrait generator. fileciteturn0file0L85-L113

## Generate assets

From the repository root:

```powershell
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github Samruddhi192105 -o assets/radar-langs --limit 7 --curve 0.4 --exclude "Shell,Makefile,Dockerfile"
python scripts/cards.py --user Samruddhi192105 --out assets
```

For the dot-matrix portrait, put your photo in the root as `me.jpg` and run:

```powershell
python scripts/dotify.py me.jpg -o assets/portrait --cols 100 --equalize --detail 0.5 --color
```

The guide recommends background removal, equalization, 100 columns and detail 0.5 for its portrait. fileciteturn0file0L190-L221

## Replace these placeholders

In `README.md`:

- `YOUR_LINKEDIN`
- `YOUR_EMAIL`
- `YOUR_PORTFOLIO`
- `YOUR_DENSEPOSE_REPO`
- `YOUR_AGENT_SWARM_REPO`

## GitHub Actions

Enable:

**Settings -> Actions -> General -> Workflow permissions -> Read and write permissions**

The guide explains that write permission is needed because workflows commit generated files back to the repository. fileciteturn0file0L427-L432

## Push

```powershell
git init
git branch -M main
git add -A
git commit -m "build profile README"
git remote add origin https://github.com/Samruddhi192105/Samruddhi192105.git
git push -u origin main
```

Then run the workflows manually once from the Actions tab. fileciteturn0file0L457-L486

## Important

The guide specifically recommends testing both dark and light GitHub themes because charts can become unreadable in the opposite theme. fileciteturn0file0L170-L187
