"""Version checker functions needed in EPM"""
import semver

def wildcard_match(version, matcher):
    """Match with wildcard in version"""
    version_info = matcher.split(".")
    if len(version_info) == 3:
        if version_info[0].isdigit() and version_info[1].isdigit() and version_info[2] == "*":
            return (
                version >= (int(version_info[0]), int(version_info[1]), 0) and
                version < (int(version_info[0]), int(version_info[1])+1, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 2:
        if version_info[0].isdigit() and version_info[1] == "*":
            return (
                version >= (int(version_info[0]), 0, 0) and
                version < (int(version_info[0])+1, 0, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 1:
        if version_info[0] == "*":
            return version >= (0, 0, 0)
        else:
            raise Exception("Failed to parse matcher")
    else:
        raise Exception("Failed to parse matcher")


def test_wilcard_match():
    """Test of wildcard matcher"""
    assert wildcard_match(semver.parse_version_info("1.2.3"), "1.2.*")
    assert wildcard_match(semver.parse_version_info("1.2.0"), "1.2.*")
    assert wildcard_match(semver.parse_version_info("1.2.1000"), "1.2.*")
    assert wildcard_match(semver.parse_version_info("1.2.3"), "1.*")
    assert wildcard_match(semver.parse_version_info("1.100.0"), "1.*")
    assert wildcard_match(semver.parse_version_info("1.2.3"), "*")
    assert wildcard_match(semver.parse_version_info("0.0.1"), "*")
    assert not wildcard_match(semver.parse_version_info("1.2.3"), "1.3.*")
    assert not wildcard_match(semver.parse_version_info("1.2.3"), "2.*")
    assert not wildcard_match(semver.parse_version_info("2.3.4"), "1.2.*")
    assert not wildcard_match(semver.parse_version_info("0.0.1"), "1.2.*")

def caret_match(version, matcher):
    """Match with wildcard in version"""
    #pylint: disable=too-many-branches
    version_info = matcher.strip('^').split(".")

    if len(version_info) == 3:
        # Check if major is zero
        if version_info[0] == "0" and version[0] == 0:
            version_info = version_info[1:] + ['0']
            version = semver.VersionInfo(*version[1:3], 0, None, None)
            # Check if minor is zero
            if version_info[0] == "0" and version[0] == 0:
                version_info = version_info[1:] + ['0']
                version = semver.VersionInfo(*version[1:3], 0, None, None)
        if version_info[0].isdigit() and version_info[1].isdigit() and version_info[2].isdigit():
            return (
                version >= (int(version_info[0]), int(version_info[1]), int(version_info[2])) and
                version < (int(version_info[0]) + 1, 0, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 2:
        # Check if major is zero
        if version_info[0] == "0" and version[0] == 0:
            version_info = version_info[1:] + ['0']
            version = semver.VersionInfo(*version[1:3], 0, None, None)
        if version_info[0].isdigit() and version_info[1].isdigit():
            return (
                version >= (int(version_info[0]), int(version_info[1]), 0) and
                version < (int(version_info[0]) + 1, 0, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 1:
        if version_info[0].isdigit():
            return (
                version >= (int(version_info[0]), 0, 0) and
                version < (int(version_info[0]) + 1, 0, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    else:
        raise Exception("Failed to parse matcher")

def test_caret_match():
    """Test of caret matcher"""
    assert caret_match(semver.parse_version_info("1.2.3"), "^1.2.3")
    assert caret_match(semver.parse_version_info("1.2.4"), "^1.2.3")
    assert caret_match(semver.parse_version_info("1.3.3"), "^1.2.3")
    assert not caret_match(semver.parse_version_info("1.2.2"), "^1.2.3")
    assert not caret_match(semver.parse_version_info("2.0.0"), "^1.2.3")

    assert caret_match(semver.parse_version_info("0.2.4"), "^0.2.3")
    assert not caret_match(semver.parse_version_info("0.3.0"), "^0.2.3")
    assert not caret_match(semver.parse_version_info("0.2.2"), "^0.2.3")

    assert caret_match(semver.parse_version_info("0.0.3"), "^0.0.3")
    assert not caret_match(semver.parse_version_info("0.0.4"), "^0.0.3")

    assert caret_match(semver.parse_version_info("0.1.0"), "^0.1")
    assert caret_match(semver.parse_version_info("0.1.2"), "^0.1")
    assert not caret_match(semver.parse_version_info("0.2.0"), "^0.1")

    assert caret_match(semver.parse_version_info("1.2.3"), "^1.2")
    assert not caret_match(semver.parse_version_info("2.0.0"), "^1.2")

    assert caret_match(semver.parse_version_info("0.0.4"), "^0")
    assert caret_match(semver.parse_version_info("0.1.4"), "^0")
    assert not caret_match(semver.parse_version_info("1.0.0"), "^0")

def tilde_match(version, matcher):
    """Match with wildcard in version"""
    version_info = matcher.strip('~').split(".")

    if len(version_info) == 3:
        if version_info[0].isdigit() and version_info[1].isdigit() and version_info[2].isdigit():
            return (
                version >= (int(version_info[0]), int(version_info[1]), int(version_info[2])) and
                version < (int(version_info[0]), int(version_info[1])+1, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 2:
        if version_info[0].isdigit() and version_info[1].isdigit():
            return (
                version >= (int(version_info[0]), int(version_info[1]), 0) and
                version < (int(version_info[0]), int(version_info[1])+1, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    elif len(version_info) == 1:
        if version_info[0].isdigit():
            return (
                version >= (int(version_info[0]), 0, 0) and
                version < (int(version_info[0])+1, 0, 0)
            )
        else:
            raise Exception("Failed to parse matcher")
    else:
        raise Exception("Failed to parse matcher")

def test_tilde_match():
    """Test of tilde matcher"""
    assert tilde_match(semver.parse_version_info("1.2.3"), "~1.2.3")
    assert tilde_match(semver.parse_version_info("1.2.4"), "~1.2.3")
    assert not tilde_match(semver.parse_version_info("1.2.2"), "~1.2.3")

    assert tilde_match(semver.parse_version_info("1.2.3"), "~1.2")
    assert not tilde_match(semver.parse_version_info("1.3.0"), "~1.2")

    assert tilde_match(semver.parse_version_info("1.2.3"), "~1")
    assert not tilde_match(semver.parse_version_info("2.0.0"), "~1")


if __name__ == "__main__":
    test_wilcard_match()
    test_caret_match()
    test_tilde_match()
