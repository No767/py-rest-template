# FastAPI Template

Performance-driven FastAPI template for MLH Hackathons

## Prerequisites

You will need to install [Atlas](https://atlasgo.io/) in order to take advantage of the migrations system. In addition, it is strongly recommended to read the [Atlas Docs](https://atlasgo.io/docs) to understand the concepts and terminologies implemented.

## Setup

> [!IMPORTANT]  
> Make sure that the dev database is up. Instructions on how to operate the dev database can be found [here](#database)

### Step 1 - Create an virtualenv

A [Virtual Environment](https://docs.python.org/3/library/venv.html) is recommended to install the library, especially on Linux where the system Python is externally managed and restricts which packages you can install on it. We can make one by following the command below:

```bash
python3 -m venv .venv
```

### Step 2 - Activate the virtualenv

```bash
# Linux/MacOS
source .venv/bin/activate

# Windows
.venv/Scripts/activate.bat
```

### Step 3 - Install dependencies

We are going to be installing all of the development dependencies needed. This includes [Lefthook](https://github.com/evilmartians/lefthook), which is the Git hooks manager.

```bash
pip install -r requirements-dev.txt \
&& lefthook install
```

### Step 4 - Copy configuration templates

This template is configured through YAML, which a template of it is included in the repo. We need to copy it over and modify the values as needed.

```bash
cp config-example.yml server/config.yml
```

### Step 5 - Apply Atlas schema

This template relies on [Atlas](https://atlasgo.io/) to bring the declarative migration workflow to hackathons. This allows for rapid reiteration and prototyping.

To make the task easier, all you need to do is run the command below and follow the given prompts:

```bash
task schema-apply
```

### Step 6 - Run the server

```bash
uvicorn launcher:app --app-dir=server --reload-exclude=venv --reload
```

Alternatively, `task start` can be used as a shortcut if you have Task installed.

Once done, navigate to `127.0.0.1:8000` and verify that it works.

## Database

The database used is PostgreSQL By default, a Docker Compose file is included for spinning up these for development. Setup instructions are as follows:

### Step 1 - Copy `.env` template

Copy `docker/example.env` to `.env` within the docker folder. Modify as appropriate.

```bash
cp docker/example.env docker/.env
```

### Step 2 - Run the container

All you need to do is to run the following command:

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

To close the container once done, the following command can be used:

```bash
docker compose -f docker/docker-compose.dev.yml stop
```

> [!TIP]
> In order to make this process easier, `task dev-up` and `task dev-stop` respectively can be used to manage the state of the dev database

## Details

There are no migrations, but rather each time the server is ran, the schema file is just read and applied each time. This allows for rapid prototyping and implementation without worrying complicated migration systems like [Altas](https://atlasgo.io/) and [Flyway](https://www.red-gate.com/products/flyway/community/), thus resulting in reproducible schemas and databases. This alone was the major factor into why [Phoebe](https://devpost.com/software/phoebe-izav85) (Winning QWER Hacks 2024 project) was nearly fully operational and how the backend was finished in 16 hours.

### Credits

This template is pulled from the design and implementation of [Kanae](https://github.com/UCMercedACM/kanae), [Kaede](https://github.com/No767/kaede-server), and Diamond's [py-rest-template](https://github.com/diamondburned/py-rest-template).
