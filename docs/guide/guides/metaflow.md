# Metaflow Guide

## Recap: What can Metaflow do for you?

### Data versioning

Each execution of a Flow has a unique run ID which data artifacts are stored under.

The artifacts and metadata of each run can be fetched using the [Metaflow client API](https://docs.metaflow.org/metaflow/client).

### Scalable computing

Metaflow abstracts infrastructure making horizontally and vertically scalable cloud computing easily available to Data Scientists.

In some (not all) cases it's as easy as adding `--with batch` to the end of the command to run a flow!

### Sharing results

Data artifacts of runs can be stored and versioned not only on your machine but also to AWS S3, meaning you can share your results easily.

### Get you out of dependency hell

Ever run into a situation where one part of a project needs a package that conflicts with another?

Metaflow allows you to [specify dependencies at the flow level](https://docs.metaflow.org/metaflow/dependencies) and automatically builds a Conda environment and runs your flow in it.

### Make your pipelines easier to understand

Expressing a script as a DAG instead makes things a lot easier to understand.

Metaflow also has commands such as `show` and `output-dot` which visualise this structure.

### Checkpointing

It's annoying when your code has gotten halfway through a pipeline only to tail.

Metaflow automatically checkpoints the steps of your flow and lets you `resume` a run after fixing any issues, saving you having to re-run the whole pipeline or maintain your own checkpointing logic (that may be fraught with conflicts between different run parameters).

## Best practices

### Writing flows

-   **Naming a flow**
    -   No need to add `Flow` as a suffix, the directory structure should speak to that
    -   Don't make names too generic, e.g. if the flow trains a topic model on Arxiv paper abstracts then call it something like `ArxivAbstractTopicModel` rather than just `TopicModel`
-   **Add a test mode**

    If your flow takes more than a minute or two to run then you should always add a parameter `test_mode = Parameter("test-mode", ...)` (by convention) which will run your flow in a test mode that runs quickly, e.g. fetch/run a subset of the data.
    This facilitates both efficient code review (a reviewer can check the test mode runs successfully without having to wait hours/days for the full flow to run) and automated testing.

    We recommend that by default `self.test_mode` is either:

    -   The logical not of `current.is_production` (`default=lambda _: not current.is_production`)
    -   `True`

    If a flow is run with `--production` (`current.is_production` is `True`) then test mode functionality should not be activated!
    Whilst often the logical not of one another, `self.test_mode` and `current.is_production` are two different concepts - `self.test_mode` and `current.is_production` may both be `False` when a user wants to run a flow without affecting
    other users.

-   The only class/function in a flow file should be the Flow itself
-   Flows should use the `@project` decorator (see [workflow](#workflow)) using a consistent `name` parameter throughout the project
-   Flow steps should be as minimal as possible containing:
    -   Setup such as parsing and logging parameters or declaring context managers
    -   At most a few high-level function calls
    -   Any flow-level logic - e.g. merging artifacts
-   Add type-annotations for the data artifacts
-   Imports used within a step should always go within a step (at the top of it)

    Because metaflow has the ability to abstract infrastructure then
    different steps may run on different machines with different environments.
    `from kuebiko.pipeline.sic.utils import *` wouldn't work in a step - `kuebiko`
    isn't installed/packaged in the new conda environment.

-   Avoiding saving data artifacts as dataframes (or other library-specific classes) favouring standard Python data-structures instead.

    Python data-structures do not impose the Pandas dependency on the
    downstream consumer of the data who may be working in an environment
    where Pandas isn't available (e.g. AWS lambda) or may have a
    different version of Pandas which when your artifact is loaded
    may subtly differ or fail to load.
    If dataframes are persisted as regular Python data-structure, the
    downstream consumer can still generate a dataframe if they want.

-   Only use Metaflow's conda decorators when you definitely need them
-   Docstrings for steps:
    -   Always for `start` and `end` - their name cannot convey any information about what the step does
    -   For any step whose name cannot convey the essence of the step or for complex steps (steps that are more than one or two well documented function calls)

### Workflow

-   Use `local` datastore during development

    Either pass `--datastore=local` when running a flow or add `METAFLOW_DEFAULT_DATASTORE=local` to `.envrc` to change the default datastore.

    This reduces the overhead to run a flow but means the results are local to your machine (the metadata of the run is still stored in an AWS RDS instance).

-   Use `datastore=s3` with `--production` to run your flow such that the artifacts can be seen by another user.
-   Use the namespace relating to your `@project` name, e.g. if you're using `@project(name="kuebiko")` for your flows, use `metaflow.namespace("project:kuebiko")`
    -   Setting that in `kuebiko/__init__.py` means it gets set whenever you use a getter

## Things to watch out for

### Gotchas

-   You cannot save functions as data artifacts, they get ignored. You can however save data artifacts with functions inside, e.g. `self.artifacts = {"key": lambda _: "value"}`

### Bugs

Here are a bugs you may encounter:

-   Using `resume` on a failed flow that uses `metaflow.S3` may fail/be inconsistent
    -   https://github.com/Netflix/metaflow/issues/664
-   Metaflow's Conda decorators don't work with Python 3.9
    -   https://github.com/Netflix/metaflow/issues/399

### Poor errors

Here are errors you may encounter which are uninformative:

-   `TypeError: Can't mix strings and bytes in path components` - Use of `metaflow.S3` with an incorrect metaflow profile
