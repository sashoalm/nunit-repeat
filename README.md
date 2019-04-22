# Overview

This script will call NUnit, then examine its TestResult.xml to see if there are any failed tests. If there are, it will execute it again only for the failed tests, and then it will see if any are successful and update the loaded TestResult.xml accordingly. It will repeat this until all tests are successful or it has run out of retries.

## Command line

`--retries <n>`: How many times to retry the tests if there are still failing tests. If ommitted the default value is 3.

`--`: Indicates that the arguments afterwards should be passed to nunit.

## Test project

The script comes with an example nunit project that mocks failing tests by keeping "counters" in files. It uses files so that the counters are preseved between reruns. 

## Example usage

First build the MockFailingTests project that comes with the script, then execute this:

    python nunit-repeat.py --max-retries 3 -- .\MockFailingTests\packages\NUnit.ConsoleRunner.3.10.0\tools\nunit3-console.exe .\MockFailingTests\MockFailingTests\bin\Debug\MockFailingTests.dll
