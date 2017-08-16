class BaseBackendEvent(object):
    def __init__(self, *args, **kwargs):
        self.event_time = kwargs['event_time']
        self.replica_group = kwargs['replica_group']


class BackendConnect(BaseBackendEvent):
    def __init__(self, *args, **kwargs):
        super(BackendConnect, self).__init__(*args, **kwargs)
        self.additional_info = kwargs['additional_info']

    def __repr__(self):
        return "BackendConnect(event_time={}, backend={}, replica_group={})".\
            format(self.event_time, self.additional_info, self.replica_group)


class BackendRequest(BaseBackendEvent):
    def __repr__(self):
        return "BackendRequest(event_time={},replica_group={})".format(
            self.event_time, self.replica_group)


class BackendOk(BaseBackendEvent):
    def __repr__(self):
        return "BackendOk(event_time={},replica_group={})".format(
            self.event_time, self.replica_group)


class BackendError(BackendConnect):
    def __repr__(self):
        return "BackendError(event_time={}, error={}, replica_group={})".\
            format(self.event_time, self.additional_info, self.replica_group)
