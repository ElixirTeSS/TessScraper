__author__ = 'milo'

import uuid

class OrgUnit():
    def __init__(self):
        self.id = uuid.uuid4()
        self.name = None
        self.title = None
        self.image_url = None
        self.description = None
        self.state = None

    # CKAN expects some JSON to be sent when creating new objects.
    def dump(self):
        data = {#'id': str(self.id),
                'name': self.name,
                'title': self.title,
                'image_url': self.image_url,
                'description': self.description,
                'state': self.state
                }
        return data
