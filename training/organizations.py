class OrgUnit:
	def __init__(self):
	        self.id = uuid.uuid4()
	        self.title = None
        	self.name = None
	        self.description = None
	        self.image_url = None

	def dump(self):
		data = {
		'name': self.name,
		'title': self.title,
		'description': self.description,
		'image_url': self.image_url
		}
		return data
