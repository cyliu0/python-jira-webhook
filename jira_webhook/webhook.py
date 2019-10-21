import collections

from flask import abort, request, jsonify, make_response


class JiraWebhook(object):
    """
    Construct a JIRA Webhook

    :param app: Flask app that host the webhook
    :param endpoint: the endpoint for the registererd URL rule
    """

    def __init__(self, app, endpoint="/jira"):
        app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=self._post_receive, methods=["POST"])
        self._hooks = collections.defaultdict(list)

    def hook(self, event_type="jira:issue_updated"):
        """
        Register a function as a JIRA Webhook. Multiple hooks can be registered for a given type,
        but the order in which they are invoke is unspecified.

        :param event_type: The event type this hook will be invoked for.
            Refer to https://developer.atlassian.com/server/jira/platform/webhooks/#configuring-a-webhook
        """

        def decorator(func):
            self._hooks[event_type].append(func)
            return func

        return decorator

    def _post_receive(self):
        """Callback from Flask"""
        data = request.get_json()
        if data is None:
            abort(make_response(jsonify(error="Request body must contain json"), 400))

        event_type = data.get("webhookEvent")
        if event_type is None:
            abort(make_response(jsonify(error="Request body must contain webhookEvent"), 400))

        for hook in (self._hooks[event_type]):
            hook(data)

        return "", 200
