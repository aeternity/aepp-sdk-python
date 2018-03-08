# How to install an Epoch test network on Ubuntu

Tested on Ubuntu 10.10 and 10.04. This will install a 3-node system for local testing. Optionally you may choose to speed up mining in order to get faster results, and/or restrict mining to one node to make tracking what happens on each node easier.

## Step 1 -- install ESL Erlang 20, jq and libsodium on your system.

Don't use the Ubuntu-provided packages. They cause compile errors.

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


## Step 2 -- get the source

`git clone git@github.com:aeternity/epoch.git`

### Step 2.1 -- speed up block mining (optional)

In the file epoch/apps/aecore/src/aec_governance.erl change the line 

`-define(EXPECTED_BLOCK_MINE_RATE, 300000). %% 60secs * 1000ms * 5 = 300000msecs`

to something like 

`-define(EXPECTED_BLOCK_MINE_RATE, 15000). %% 15secs * 1000ms = 15000msecs`

before compiling

### Step 2.2 -- mine (you need to do some mining).

the sys.config files under config/dev config/dev2 and config/dev3 describe the behaviour of the 3 test nodes. By default none of the nodes mine. Making dev1 mine enables you to play with spending and see easily what is going on. Change '{autostart, false}' under `aecore` to `true` in config/dev1/sys.config for this behaviour.

## Step 3 Build and run

```
cd epoch/
make multi-build
```
This will create a directory \_build under epoch. Under this are dev1/rel/epoch and so forth.

`make multi-start` will start the three. You can ignore the ulimit messages for a network of this size.

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

We have provided 3 convenience scripts which enable you to switch between the instances:

dev1.sh:
```
export AE_LOCAL_PORT=3013
export AE_LOCAL_INTERNAL_PORT=3113
export AE_WEBSOCKET=3114
. ${BASH_SOURCE%/*}/aeternity-functions.sh
```
dev2.sh
```
export AE_LOCAL_PORT=3023
export AE_LOCAL_INTERNAL_PORT=3123
export AE_WEBSOCKET=3124
. ${BASH_SOURCE%/*}/aeternity-functions.sh
```
dev3.sh
```
export AE_LOCAL_PORT=3033
export AE_LOCAL_INTERNAL_PORT=3133
export AE_WEBSOCKET=3134
. ${BASH_SOURCE%/*}/aeternity-functions.sh
```

You can now play with æternity:

```
$. ../dev2.sh
$aepub_key 
ak$3auB9artUQWFJifbU66LQ9iahEdzTAbmpsC2xfVizRxFnxbiV7KVj2jS572pDG3x8KCcvcTQETivd4BsVBPbv3k8QdfEbC
$. ../dev1.sh
$aebalance 
250
$aespend-tx 'ak$3auB9artUQWFJifbU66LQ9iahEdzTAbmpsC2xfVizRxFnxbiV7KVj2jS572pDG3x8KCcvcTQETivd4BsVBPbv3k8QdfEbC' 200 1
{}$balance 
260
260
$aebalance 
70
$. ../dev2.sh
$aebalance 
200
```

## Getting the python part to run

make a python3 virtual environment where you can install all depencencies:

```
# go to python dir
cd dev-tools/python
# create the virtual env in a folder called "venv"
virtualenv -p python3 venv
# activate the virtual environment
source venv/bin/activate
# install the dependencies
pip install -r requirements.txt
```

