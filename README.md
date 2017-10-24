# ECS Stat

Probe the status of an AWS ECS cluster and access the logs of a specific
container.

This is a work in progress.

## Installation

Well, there's really not much to install yet. ECS Stat can be used via
virtualenv like this:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python ecs_stat
```

## Usage

You might have to set a default region (i.e. `AWS_DEFAULT_REGION` env var), for
boto to be happy.

```
usage: ecs_stat [-h] [--tail_logs TAIL_LOGS]

ECS status

optional arguments:
  -h, --help            show this help message and exit
  --tail_logs TAIL_LOGS
                        <cluster_n>,<service_n>,<task_n>,<container_n>

```

## Status

I haven't been working on this project for a long time, so some AWS APIs might
have changed in the meanwhile.

My plan was to add proper testing with [moto](https://github.com/spulec/moto)
and for this I've [improved](https://github.com/spulec/moto/pull/635) the ECS
support in moto.
