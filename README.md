# JLITE Artifact

## Build and Use of JLITE

### Dependencies

To build JLITE, you need the following dependencies installed:

- CMake >= 3.0
- GCC >= 9.0
- JDK 8

### Build & Install

```
cd jlite
export JAVA_HOME=<JAVA_HOME_FOR_JDK8>
./build.sh
```

Load the environment to use the installed JLITE:

```
cd jlite
# load the environment variables
source env.sh
```

### How to use JLITE

To use JLITE, you need to complete each step of the **Build & Install**
Usage:

```
cd jlite
./run_server.sh

LD_PRELOAD=/path/to/jlite/install/lib/libpreload.so LD_LIBRARY_PATH=/path/to/jlite/install/lib/ java -agentpath:/path/to/jlite/install/lib/libagent.so -javaagent:/path/to/jlite/agent-jar-with-dependencies.jar[="<args>"] [-jar] <JAVA_APP>
```

#### Arguments

- -m, --mode                    base, use
  - base mode:  Trace `new`, `free`, `aastore`, `putfield`, `gc-memmove` information.
  - use mode:   Trace `new`, `use` information. If `use` mode is enabled, `--use-candidate-file` option is necessary.

#### Other Requirements

A file `candidate.txt` that contains classes you want to trace in `use` mode. Format is as followed.

```
java/lang/ArrayList
java/lang/String
```

#### Bootstrap mode

Only bootstrap mode can trace some java standard library. 

Add java argument `-Xbootclasspath/a:/path/to/JLITE/agent-jar-with-dependencies.jar` and you can enable bootstrap mode.

After running of JLITE, a directory named `data-<pid>` is generated.

### Analysis Scripts

Before analysis, trace needs to be processed. Analysis related scripts can be found at `jlite/scripts`.

#### Redundant Stack-bound Objects(rso.py) and Recurring Object Assignments(roa.py)

These analysis can be done at reference mode.

Usage:

```
cd data-<pid>
csv2db <pid>
python3 csv2db.py
python3 build_owner.py
python3 <analysis.py>
```

`pid` means pid of jvm. 

#### Unused Object Allocation(uoa.py) and Immutable Read-Only Objects(iro.py)

These analysis can be done at use mode.

Usage:

```
cd data-<pid>
csv2db <pid>
python3 csv2db.py
python3 build_owner.py
python3 build_use.py
python3 <analysis.py>
```

#### Superfluous Objects Allocation(soa.py)

This analysis can be done at reference mode, and data process of soa is not compatible with rso and roa.

Usage:

```
cd data-<pid>
addr2id
csv2db <pid>
python3 csv2db.py
python3 <analysis.py>
```

## Overhead Evaluation

It may take long time to run overhead evaluation.

### Requirements

- Jdk 8
- Jdk 11
- python3 
  - numpy
  - scipy
  - matplotlib



### Preparation of Benchmarks

```
cd <root-of-project>
. env.sh
cd benchmarks
./download.sh
```

### Run of Benchmarks

```
export JAVA8_HOME=<JAVA_HOME_OF_JDK8>
export JAVA11_HOME=<JAVA_HOME_OF_JDK11>
cd <root-of-project>
. env.sh
cd benchmarks
./run.sh <times-to-run>
```

### Process of Log File

```
cd <root-of-project>
. env.sh
cd benchmarks
./process.sh
```

Two pdf file will be generated.