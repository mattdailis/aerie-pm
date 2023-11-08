# aerie-pm

`pm` stands for "pro(ject|duct) management". This command line utility is meant to help customize and automate parts of our workflow.

The source of truth is, for now, still the Aerie GitHub project. `pm` will create a cache of relevant information in `~/.pm/pm.json` to limit network calls to github.com. This cache improves command response times, allows for offline work, and avoids triggering github.com rate limiting.

To update the cache, periodically run `pm fetch --items`. This will download any issues or prs that were updated since last time you ran `pm fetch --items`. It will also download every single item in the Aerie github project, since as of writing there does not seem to be a way to filter these by updated time.

## Installation
Prerequisite software:
- git
- [github cli](https://cli.github.com/)
- Python 3.9.6 (other versions may work, but your mileage may vary)

For now, the expectation is that if you're installing `pm`, you're also going to be tweaking the code. For this reason, start out by cloning this repository

```shell
git clone git@github.com:mattdailis/aerie-pm.git 
```

Go into the `aerie-pm` folder and create a virtual environment
```shell
cd aerie-pm
python3 -m venv venv
```

Now source this venv, and install dependencies
```shell
source venv/bin/activate
pip install -r requirements.txt
```

Finally, install the repository itself in "editable" mode
```shell
pip install -e .
```

This will generate an executable at `aerie-pm/venv/bin/pm`. You can add it to your path, so you won't need to source `venv/bin/activate` in the future.

```shell
echo "export PATH=\"$(pwd)/venv/bin:\$PATH\"" >> ~/.zshrc
```
