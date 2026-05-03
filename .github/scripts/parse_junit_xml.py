#!/usr/bin/env python3
"""Parse JUnit XML test results and display summary."""
import sys
import xml.etree.ElementTree as ET


def parse_junit_xml(junit_file: str) -> dict:
    """
    Parse JUnit XML file and extract test statistics.

    Args:
        junit_file: Path to JUnit XML file

    Returns:
        Dictionary with test statistics
    """
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()

        # Handle both testsuite and testsuites root elements
        if root.tag == 'testsuites':
            ts = root.find('testsuite')
        else:
            ts = root

        if ts is not None:
            tests = ts.get('tests', '0')
            failures = ts.get('failures', '0')
            errors = ts.get('errors', '0')
            return {
                'tests': tests,
                'failures': failures,
                'errors': errors,
                'success': True,
                'message': f'**Tests:** {tests} total, {failures} failed, {errors} errors'
            }
        return {
            'success': False,
            'message': '**Tests:** Unable to parse JUnit XML'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'**Tests:** Error parsing JUnit XML: {e}'
        }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <junit.xml>")
        sys.exit(1)

    result = parse_junit_xml(sys.argv[1])
    print(result['message'])
    sys.exit(0 if result.get('success', False) else 1)
