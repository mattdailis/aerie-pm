# aerie-pm

`pm` stands for "pro(ject|duct) management". This command line utility is meant to help customize and automate parts of our workflow.

The source of truth is, for now, still the Aerie GitHub project. `pm` will create a cache of relevant information in `~/.pm/pm.json` to limit network calls to github.com. This cache improves command response times, allows for offline work, and avoids triggering github.com rate limiting.

To update the cache, periodically run `pm fetch --items`. This will download any issues or prs that were updated since last time you ran `pm fetch --items`. It will also download every single item in the Aerie github project, since as of writing there does not seem to be a way to filter these by updated time.

## Installation
Prerequisite software:
- git
- [github cli](https://cli.github.com/) (should be accessible via the PATH environment variable as `gh`)
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

Next, install dependencies in this virtual environment
```shell
./venv/bin/pip install -r requirements.txt
```

Finally, install the repository itself in "editable" mode
```shell
./venv/bin/pip install -e .
```

This will generate an executable at `aerie-pm/venv/bin/pm`. Let's add it to the path to make it accessible as `pm`:

```shell
echo "export PATH=\"$(pwd)/venv/bin:\$PATH\"" >> ~/.zshrc
```

Check that the installation was successful by running `pm --help`
```shell
> pm --help
Usage: pm [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  backlog
  csv
  fetch
  issues
  items
  standup
  view
```