import random
import os

import dotenv
import vk_api

from . import BaseSource
from .. import exceptions
from .. import rules_setup

dotenv.load_dotenv()

vk_requests = vk_api.VkApi(token=os.environ['VK_PARSER_TOKEN']).get_api()


class Vk(BaseSource):
	_types = {'photo': 'photo',
	          'video': 'video'}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.domain = self.link[self.link.rfind(r'/') + 1:]
		# Specify types to vk attachment types
		self._included_types = {y for i in self._included_types if (y := Vk._types.get(i))}
		self._excluded_types = {y for i in self._excluded_types if (y := Vk._types.get(i))}

		self.cards_quantity = None

	def get_cards_quantity(self):
		return vk_requests.wall.get(domain=self.domain, count=1)['count']

	def set_cards_quantity(self, quantity=None):
		if quantity is None:
			self.cards_quantity = self.get_cards_quantity()
		else:
			self.cards_quantity = quantity

	def get_random_card(self):
		def extract_content_from_attachment(attachment):
			match attachment['type']:
				case 'photo':
					return attachment[attachment['type']]['sizes'][-1]['url']
				case 'video':
					video_id = str(attachment[attachment['type']]['owner_id'])
					video_id += '_' + str(attachment[attachment['type']]['id'])

					return vk_requests.video.get(videos=video_id)['items'][0]['player']

		self.set_cards_quantity()
		if self.cards_quantity == 0:
			raise exceptions.NoAnyPosts

		try:
			attachments = vk_requests.wall.get(domain=self.domain,
			                                   offset=random.randrange(self.cards_quantity),
			                                   count=1)['items'][0]['attachments']
		except KeyError:
			return self.get_random_card()

		# If attachments are found, then get the random one
		random.shuffle(attachments)
		for a in attachments:
			if a['type'] not in rules_setup.excluded_types:
				if rules_setup.included_types:
					if a['type'] not in rules_setup.included_types:
						continue
				return extract_content_from_attachment(a)

		return self.get_random_card()
