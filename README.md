# python-aodndata

![python-aodndata](https://github.com/aodn/python-aodndata/workflows/python-aodndata/badge.svg)
[![coverage](https://codecov.io/gh/aodn/python-aodndata/branch/master/graph/badge.svg)](https://codecov.io/gh/aodn/python-aodndata)

This repository holds per-facility Python pipeline code, for example handlers, destination path functions and any other code specific to a given facility and/or pipeline.

The code extends the [aodncore](https://github.com/aodn/python-aodncore) project which is treated as an upstream library, providing primarily the HandlerBase parent class, which provides all of the common handler capabilities and essentially implements the entire "generic handler".

Facility/pipeline specific handlers are then created as a subclass of HandlerBase, and act to configure, extend and/or modify the behaviour as appropriate for the specific pipeline.

For example, a child class may do one or more of the following:
* define how the destination path is determined for the file(s) being handled (i.e. a dest_path function)
* restrict which file extensions/types are allowed to be handled
* determine which [compliance checks](https://github.com/ioos/compliance-checker) are performed against files (if applicable)
* in case of a "multiple file" handler (e.g. a ZIP or manifest file), determine which files are included/excluded, e.g. process all NC files in a ZIP but not TXT files, or define on an individual file basis which ones are harvested and/or uploaded and/or archived
* determine who is notified in case of handler error (or success)

# User Guide

It is highly recommended to use the [PyCharm IDE](https://www.jetbrains.com/pycharm/) for developing on this code base, as it provides many useful features out of the box, such as good unit test integration, real time code quality checking, automatic completion, and the usual basic IDE debugging capabilities such as setting breakpoints and syntax highlighting.

## Setting up the development environment

### Pre-requisites
1. Ensure the [aodn/chef](https://github.com/aodn/chef) repository is checked out (directory will be referred to as **${CHEF_REPO}**), and the usual pre-requisites for running the PO box are met
1. Ensure that your GitHub keys are in place so that you have write access to the **python-aodndata** repository on GitHub
1. Provision the PO box using the **bin/pipeline-box.sh** script, so that the required repositories are checked out and the PO box is ready for use
1. Install the boto3 and virtualenv packages into your system Python environment:

    ```bash
    $ sudo pip install boto3 virtualenv
    ```

### Virtual environment setup
Developing in a Python virtual environment is the best choice to isolate the project from external Python dependencies (e.g. those installed with the operating system). 

1. In a terminal, browse to the **${CHEF_REPO}/src/python-aodndata**:

    ```bash
    $ cd ${CHEF_REPO}/src/python-aodndata
    ```
    
1. Execute the **setup_virtualenv.sh** script:

    ```bash
    $ scripts/setup_virtualenv.sh
    Downloading dependencies...
    Creating virtual environment...
    Installing dependencies into virtual environment...
    Virtual environment successfully created at: python-aodndata-virtualenv

    To use:
      * Configure PyCharm project interpreter as: /home/me/github/chef/src/python-aodndata/python-aodndata-virtualenv/bin/python
      * Activate in shell environment: $ source /home/me/github/chef/src/python-aodndata/python-aodndata-virtualenv/bin/activate

    ```

    Note: by default, the virtual environment will source AODN dependencies (e.g. aodntools, aodncore) from the production repository.
        If you want to test a package which is at a different promotion stage,  you can override this by setting the `STAGE` environment
        to either `rc` or `build`:
        
       ```bash
       $ export STAGE=rc
       $ scripts/setup_virtualenv.sh
       ```
       
1. Make note of the path to the Python interpreter output by the script (this is needed for the next step)

### IDE setup
1. Open PyCharm
1. Click '_Open_' and browse to the **python-aodndata** repository checked out by the PO box script (i.e. **${CHEF_REPO}/src/python-aodndata**)
1. Click '_File_' -> '_Settings_' and browse to '_Project: python-aodndata_'-> '_Project Interpreter_'
1. Click the 'cog' icon in the top right of the window, select '_Add Local..._', '_Existing Environment_', browse to or paste the path to the Python interpreter from the virtual environment setup step, and press '_OK_' and '_OK_' to save the configuration
1. Confirm that the unit tests for the project run correctly by right-clicking on the **test_aodndata** directory and '_Run Unittests in test_aodndata_'

## Writing code

The best way to get started writing a handler is to create the handler class itself along with an associated unit test class in order to easily run the handler with arbitrary inputs. This makes it possible to make small changes and immediately run the handler in the IDE to observe the results, long before trying to deploy the code to a running pipeline.

### Package structure
Each facility is given it's own module namespace, **aodndata.facility_name** in which to define objects relating specifically to that facility (for example, the handler classes themselves, destination path functions or any other miscellaneous supporting code).

For example, the moorings facility occupies the **aodndata.moorings** namespace, and defines the following objects:

```python
# a handler class; a sub-class of HandlerBase extended to specifically support moorings input files
from aodndata.moorings.handlers import MooringsHandler  

# helper class used in determining the destination path
from aodndata.moorings.classifiers import MooringsFileClassifier

# a 'dest_path' function, which given the path to a file, returns the _destination path_, i.e. the path to which the file will be published on S3
from aodndata.moorings.classifiers import dest_path_anmn_nrs_realtime
dest_path = dest_path_anmn_nrs_realtime('test_aodndata/common/IMOS_ANMN-NRS_MT_20161109T231108Z_NRSMAI_FV00_NRSMAI-Surface-21-2016-11-MET-realtime.nc')

print(dest_path)
IMOS/ANMN/NRS/REAL_TIME/NRSMAI/Meteorology/IMOS_ANMN-NRS_MT_20161109T231108Z_NRSMAI_FV00_NRSMAI-Surface-21-2016-11-MET-realtime.nc
 ```

### Handler quick start

1. If there isn't already a relevant facility subpackage under **aodndata**, create one (in accordance with the preferred [naming conventions](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)). A package is a directory containing an (often empty) **\_\_init\_\_.py** file, and allows clean arrangement of code into a namespace. The structure is arbitrary, however if in doubt, you may wish to create a **handlers.py** module in the directory to contain the handler code as a starting point:

    ```bash
    ${CHEF_REPO}/src/python-aodndata/aodndata$ find myfacility/
    myfacility/
    myfacility/__init__.py  # empty file
    myfacility/handlers.py
    ```
    
1. Create a handler class in **handlers.py**:

    ```python
    import os
    from aodncore.pipeline import HandlerBase
    
    
    class MyFacilityHandler(HandlerBase):
        @staticmethod
        def dest_path(filepath):
            basename = os.path.basename(filepath)
            return "IMOS/parent/path/that/is/always/the/same/{basename}".format(basename=basename)
    ```

1. Add the handler to the _ENTRY_POINTS['pipeline.handlers']_ list in **setup.py**. This is not required for unit testing, but is required to "advertise" the class as an available handler under the **pipeline.handlers** entry point group once the **aodndata** package has been deployed:

    ```python
    ENTRY_POINTS = {
        'pipeline.handlers': [
            ...
            'MyFacilityHandler = aodndata.myfacility.handlers:MyFacilityHandler',
            ...
        ],
    ...
    }
    ```

1. Create a unit test subpackage under the **test_aodndata** directory. Prefix the module you create with '**test_**'. You may wish to add some example data files for use in testing, for example, an example of a *good* file which should always pass the tests and an example of a *bad* file which will allow testing a failure scenario, e.g.

    ```bash
    ${CHEF_REPO}/src/python-aodndata/test_aodndata$ find myfacility/
    myfacility/
    myfacility/__init__.py  # empty file
    myfacility/test_handlers.py
    myfacility/myfacility_good.nc  # file expected to succeed
    myfacility/myfacility_bad.nc  # file expected to fail, e.g. non-compliant, invalid format etc.
    ```
    
1. Create a handler test case in **test_handlers.py**:

    ```python
    import os
    
    from aodncore.pipeline.exceptions import ComplianceCheckFailedError
    from aodncore.testlib import HandlerTestCase
    
    from aodndata.myfacility.handlers import MyFacilityHandler
    
    TEST_ROOT = os.path.join(os.path.dirname(__file__))
    GOOD_NC = os.path.join(TEST_ROOT, 'myfacility_good.nc')
    NOT_A_NETCDF = os.path.join(TEST_ROOT, 'not_a_netcdf_file.nc')
    
    
    class TestMyFacilityHandler(HandlerTestCase):
        """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
           unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
           scenarios.
        """
        #This is a "boilerplate" method that must appear in each test case in order to correctly inherit from the HandlerTestCase class
        def setUp(self):
            # set the handler_class attribute to your handler (as imported above)
            self.handler_class = MyFacilityHandler
            super(TestMyFacilityHandler, self).setUp()
    
        def test_good_file(self):
            # we expect this to succeed, so if the handler experiences an error, it is considered a
            # "failed test"
            handler = self.run_handler(GOOD_NC)
            pass
    
        def test_good_file_with_compliance_check(self):
            # we also expect this to succeed, since the test file is known be CF compliant
            handler = self.run_handler(GOOD_NC, check_params={'checks': ['cf']})
            pass
    
        def test_bad_file(self):
            # we expect this to fail with a 'ComplianceCheckFailedError' exception, since it's not actually
            # a NetCDF file since we expect this to be a failure, we use run_handler_with_exception to
            # invert the expected result, so that it treats a success as an undesired outcome, and therefore
            # a "failed test"
            handler = self.run_handler_with_exception(ComplianceCheckFailedError, NOT_A_NETCDF)
            pass

    ```

1. You can now test your handler by simply running the unit tests. There are several ways to run them in the IDE, but you can get fine-grained control over which tests are run by opening the test module, and right-clicking on the test class and clicking _'Run unittests for Unittests for test_handlers.TestMyFacilityHandler'_, or even the individual test methods. This enables the handler class itself to be largely configured
and tested before leaving the IDE, and proceeding on to integration testing, to run the handler in a "deployed" context.

1. For further documentation relating to available handler parameters, and how a handler class works, refer to the upstream [aodncore documentation](https://github.com/aodn/python-aodncore). 
Handler parameters consist of a single positional parameter, which is always 'input_file', a 'config' object (set automatically in both unittests and when deployed), an optional Celery task parameter, set when run under a Celery task, and a series of keyword arguments to control the handler behaviour.
For example, as at time of writing, the user configurable handler parameters are as follows:

    ```
    :param allowed_extensions: list of allowed extensions for the input file
    :param archive_input_file: flag to determine whether the original input file is archived
    :param archive_path_function: function reference or entry point used to determine archive_path for a file
    :param check_params: list of parameters to passed through to the compliance checker library
    :param dest_path_function: function reference or entry point used to determine dest_path for a file
    :param exclude_regexes: list of regexes that files matching include_regexes must *not* match to be 'eligible'
    :param harvest_params: keyword parameters passed to the publish step to control harvest runner parameters
    :param harvest_type: determine which harvest type will be used (supported types in harvest module)
    :param include_regexes: list of regexes that files must match to be 'eligible'
    :param notify_params: keyword parameters passed to the notify step to control notification behaviour
    :param upload_path: original path of file (for information only, e.g. notifications)
    :param resolve_params: keyword parameters passed to the publish step to control harvest runner parameters
    :param kwargs: allow additional keyword arguments to allow potential for child handler to use custom arguments
    ```

### Integration testing
It is perfectly possible to perform this setup and IDE testing without the use of the PO box and chef repo, however the key reason to do this is to shortcut the integration testing and leverage the capabilities of Vagrant/Virtualbox shared folders to source the Python libraries directly from the **same directory** that you are editing in the IDE.

This allows for a much more rapid turnaround in getting your "work in progress" code to actually run in a live development environment (in this case, the PO box).

Note: the following assumes that you are running the PO box from the same **${CHEF_REPO}** as referred to above in the IDE setup

1. Add a watch configuration to the **imos_po_watches** databag in Chef. A watch configuration defines an individual pipeline, and consists of the following JSON keys:

    1. **path**: types: JSON=array, Python=list : list of incoming directory paths to be watched, and have incoming files routed to this pipeline
    1. **handler**: types JSON=string, Python=str : name of the handler class to use (the handler class is resolved by looking for this string in the **pipeline.handlers** entry point group and retrieving the corresponding handler object)
    1. **params**:  types JSON=object, Python=dict : parameters passed directly through to the handler class **_\_\_init\_\__** method as keyword arguments

    **${CHEF_REPO}/private-sample/data_bags/imos_po_watches/MYFACILITY.json**

    ```json
    {
      "id": "MYFACILITY",
      "path": [ "myfacility" ],
      "handler": "MyFacilityHandler",
      "params": {
        "allowed_extensions": [
          ".nc"
        ],
        "check_params": {
          "checks": ["cf"]
        }
      }
    }
    ```
 
1. Edit the ${CHEF_REPO}/private-sample/nodes/po.json file and add the watch in the _data_services_ -> _pipeline_2_watches_ array
 
    ```json
        ...
            "data_services": {
                ...
                "pipeline_2_watches": [
                    ...
                    "MYFACILITY",
                    ...
                ],
        ...
    ```
    
1. Provision the PO box

    ```bash
    cd ${CHEF_REPO}
    bin/po-box.sh
    ```

1. When you make a change to the **aodndata** code, it is simply necessary to restart the individual pipeline in order for the changes to be applied to the PO box environment:

```bash
$ sudo supervisorctl restart pipeline_worker_MYFACILITY
```
