


class Event(object):
    def __init__(self,event_type,data,source,client):
        self.type = event_type
        self.data = data
        self.source = source
        self.client = client

    def __str__(self):
        newdata = dict(self.data)
        for key in ['password','token']:
            if key in newdata:
                newdata[key] = '***'

        return 'Event: {}, data: {}, source: {}, client: {}'.format(self.type,newdata.__repr__(),self.source.__class__.__name__,self.client.__repr__())


