import pkg_resources


def get_version():
    '''Retrieves and returns the package version details.
    '''
    package = pkg_resources.require('pipaystack')
    return package[0].version