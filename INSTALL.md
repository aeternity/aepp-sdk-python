# How to install an Epoch test network on Linux

Tested on Ubuntu 17.10, Ubuntu 17.04 and Fedora 27. This will install a 3-node
system for local testing. Optionally you may choose to speed up mining in order
to get faster results, and/or restrict mining to one node to make tracking what
happens on each node easier.

The Ubuntu instructions will compile and run directly on the OS, whereas the
Fedora instructions will use Docker.

## Step 1 -- Dependencies

### Ubuntu

We'll install ESL Erlang 20, jq and libsodium on your system.

Don't use the Ubuntu-provided Erlang packages. They cause compile errors.
A usable version is provided by Erlang Solutions.

```wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
sudo dpkg -i erlang-solutions_1.0_all.deb
sudo apt-get update
sudo apt-get install esl-erlang
rm erlang-solutions_1.0_all.deb
```

Install libsodium

```
sudo apt-get install libsodium-dev
```

Also, install jq, which is needed by the bash scripts to interact with the local test nodes:

```
apt-get install jq
```

### Fedora

On Fedora, we'll install Docker CE, docker-compose and set up the current user so
it can connect to the Docker daemon.

```
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-compose
```

We'll add the current `$USER` to the `docker` system group created by the
previous installation. If this wasn't already the case, `newgrp` will make sure
the change is at least adapted in the current terminal session - to get this
change to apply everywhere else, the user has to quit the current desktop
session and log in, again.

```
sudo usermod -a -G docker $USER
newgrp docker
```

Enable and start the Docker daemon.

```
sudo systemctl enable docker
sudo systemctl start docker
```

## Step 2 -- get the source

`git clone git@github.com:aeternity/epoch.git`

### Step 2.1 -- speed up block mining (optional)

In the file epoch/apps/aecore/src/aec_governance.erl change the line 

`-define(EXPECTED_BLOCK_MINE_RATE, 300000). %% 60secs * 1000ms * 5 = 300000msecs`

to something like 

`-define(EXPECTED_BLOCK_MINE_RATE, 15000). %% 15secs * 1000ms = 15000msecs`

before compiling

### Step 2.2 -- mine (you need to do some mining).

The sys.config files under config/dev config/dev2 and config/dev3 describe the
behavior of the 3 test nodes. By default none of the nodes mine. Making dev1
mine enables you to play with spending and see easily what is going on. Change
'{autostart, false}' under `aecore` to `true` in config/dev1/sys.config for this
behavior.

## Step 3 Build and run

### Ubuntu (bare metal)

```
cd epoch/
make multi-build
```
This will create a directory \_build under epoch. Under this are dev1/rel/epoch and so forth.

`make multi-start` will start the three. You can ignore the ulimit messages for
a network of this size.

```
$ make multi-start
make[1]: Entering directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
WARNING: ulimit -n is 1024; 24576 is the recommended minimum.
You are recommended to ensure the node is stopped and raise the maximum number of open files (try 'ulimit -n 24576') before starting the node.
make[1]: Leaving directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
make[1]: Entering directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
WARNING: ulimit -n is 1024; 24576 is the recommended minimum.
You are recommended to ensure the node is stopped and raise the maximum number of open files (try 'ulimit -n 24576') before starting the node.
make[1]: Leaving directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
make[1]: Entering directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
WARNING: ulimit -n is 1024; 24576 is the recommended minimum.
You are recommended to ensure the node is stopped and raise the maximum number of open files (try 'ulimit -n 24576') before starting the node.
make[1]: Leaving directory '/mnt/sdb1/newby/projects/aeternity/src/epoch'
```

### Fedora (docker-compose)

```
cd epoch
docker-compose up
```

Now that was easy, wasn't it?

## Continue in README.md!
