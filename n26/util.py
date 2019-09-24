def create_request_url(url: str, params: dict = None):
    """
    Adds query params to the given url

    :param url: the url to extend
    :param params: query params as a keyed dictionary
    :return: the url including the given query params
    """

    if params:
        first_param = True
        for k, v in sorted(params.items(), key=lambda entry: entry[0]):
            if not v:
                # skip None values
                continue

            if first_param:
                url += '?'
                first_param = False
            else:
                url += '&'

            url += "%s=%s" % (k, v)

    return url
