# Script to run nunit tests and then repeat any failed tests until we run out of retries.

import os
import sys
import subprocess
import xml.etree.ElementTree as ET

# Finds the corresponding test with the same name in another XML file.
def findCorrespondingTest(tree2, failedTest):
    test2 = tree2.findall(".//test-case[@fullname='{}']".format(failedTest.get('fullname')))
    if len(test2) != 1:
        print(failedTest.get('fullname'))
        for ii in test2:
            print(ii.get('fullname'))
        raise Exception("len(test2) != 1")
    return test2[0]

# Python XML lib doesn't show you who is the parent of a given element so we add the info ourselves.
def addParentInfo(tree):
    for child in tree:
        setParent(child, tree)
        addParentInfo(child)

# We strip the parentage info so it doesn't pollute the XML file.
def stripParentInfo(tree):
    for child in tree:
        child.attrib.pop('__my_parent__', 'None')
        stripParentInfo(child)

# Gets the parent of a given element.
def getParent(tree):
    return tree.attrib['__my_parent__']

# Sets the parent of a given element.
def setParent(tree, parent):
    tree.attrib['__my_parent__'] = parent

# Updates a parent test suite or a run of a failed test that has passed on rerun.
def updateTestResult(tree):
    tree.attrib['failed'] = str(int(tree.attrib['failed']) - 1)
    tree.attrib['passed'] = str(int(tree.attrib['passed']) + 1)
    if tree.attrib['failed'] == '0':
        tree.attrib['result'] = 'Passed'
        failureNodes = tree.findall('failure')
        for failureNode in failureNodes:
            tree.remove(failureNode)

# In-place replaces a failed test with a successful one.
def replaceTest(tree1, tree2):
    parent = getParent(tree1)
    tree1.__setstate__(tree2.__getstate__())
    setParent(tree1, parent)

# Updates the entire chain of parent test suites.
def updateParentTestSuites(testCase):
    suite = getParent(testCase)
    while suite and suite.tag == 'test-suite':
        updateTestResult(suite)
        suite = getParent(suite)

# Updates the parent test run.
def updateParentTestRun(testCase):
    run = getParent(testCase)
    while run and run.tag != 'test-run':
        run = getParent(run)
    if run:
        updateTestResult(run)

# Merges the results from a rerun into the original test.
# Any failed test that has become successful upon rerun is updated.
def mergeRerunResults(tree1, tree2):
    for failedTest in tree1.iterfind(".//test-case[@result='Failed']"):
        test2 = findCorrespondingTest(tree2, failedTest)
        if test2.attrib['result'] == 'Passed':
            replaceTest(failedTest, test2)
            updateParentTestSuites(failedTest)
            updateParentTestRun(failedTest)

# Checks whether we have any failed tests.
def hasFailedTests(tree):
    return len(tree.findall(".//test-case[@result='Failed']")) > 0

# Writes the failed tests, one per line, in testlist.txt. This file
# will be passed to nunit console runner.
def writeFailedTests(tree):
    f = open('testlist.txt', 'w')
    for failedTest in tree.iterfind(".//test-case[@result='Failed']"):
        name = failedTest.attrib['fullname']
        f.write(name + '\n')

# Retries all the failing tests, until all pass or we run out of retries.
def retryFailedTests(args, retries, resultsFile):
    # Add the testfilter to nunit's command line.
    args.append('--testlist')
    args.append('testlist.txt')
    # Load the test results from the first invocation.
    tree = ET.parse(resultsFile)
    addParentInfo(tree.getroot())
    # Run the retries.
    while retries > 0 and hasFailedTests(tree):
        retries -= 1
        writeFailedTests(tree)
        subprocess.call(args)
        mergeRerunResults(tree, ET.parse(resultsFile))
    # Write the final results.
    stripParentInfo(tree.getroot())
    tree.write(resultsFile)
    # Check if we still have failing tests.
    if hasFailedTests(tree):
        raise Exception("There are failed tests even after retrying.")

# Main function.
def main():
    args = sys.argv
    # Get the number of retries.
    try:
        retries = int(args[args.index('--max-retries') + 1])
    except:
        retries = 3
    # Get results file name
    try:
        resultsFile = args[args.index('--results-file')+1]
    except:
        resultsFile = 'TestResult.xml'
    # Get the nunit command line.
    args = args[args.index('--')+1:]
    # Invoke nunit the first time.
    subprocess.call(args)
    # Retry any failed tests.
    retryFailedTests(args, retries, resultsFile)

# Execute main function.
main()
