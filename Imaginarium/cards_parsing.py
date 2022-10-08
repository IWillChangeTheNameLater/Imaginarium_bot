import math
import random

import validators
import vk_api
from dotenv import load_dotenv
import os

from . import rules_setup
from . import exceptions
from . import game

load_dotenv()

vk_requests = vk_api.VkApi(token=os.environ['VK_PARSER_TOKEN']).get_api()


class Link:
    def __init__(self, link):
        self.link = link


class Source:
    pass


class Vk(Source):
    def __init__(self, link):
        self.link = link
        self.domain = link[link.rfind(r'/') + 1:]
        rules_setup.included_types = {y for i in rules_setup.included_types if (y := Vk.types.get(i))}
        rules_setup.excluded_types = {y for i in rules_setup.excluded_types if (y := Vk.types.get(i))}
        self.cards_num = None

    def __eq__(self, other):
        return self.link == other

    def __ne__(self, other):
        return self.link != other

    def __str__(self):
        return self.link

    def __hash__(self):
        return hash(self.link)

    # Change specified types to vk attachment types
    types = {'photo': 'photo',
             'video': 'video'}

    def get_cards_quantity(self):
        return vk_requests.wall.get(domain=self.domain, count=1)['count']

    def set_cards_quantity(self):
        self.cards_num = self.get_cards_quantity()

    def get_random_card(self):
        def extract_content_from_attachment(attachment):
            if attachment['type'] == 'photo':
                return attachment[attachment['type']]['sizes'][-1]['url']
            elif attachment['type'] == 'video':
                video_id = str(attachment[attachment['type']]['owner_id'])
                video_id += '_' + str(attachment[attachment['type']]['id'])
                return vk_requests.video.get(videos=video_id)['items'][0]['player']

        self.set_cards_quantity()
        if self.cards_num == 0:
            raise exceptions.NoAnyPosts

        try:
            attachments = vk_requests.wall.get(domain=self.domain,
                                               offset=random.randrange(self.cards_num),
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


def create_source_object(source):
    """Return an object of class "Source".
    
    Process the link to the source (email, url, etc.) and create a "Source"
    object that can be used to get some cards."""
    if validators.url(source):
        domain_name = source[source.find('/') + 2:]
        domain_name = domain_name[:domain_name.find('/')]
        domain_name = (domain_name := domain_name.split('.'))[math.ceil(len(domain_name) / 2) - 1]

        if domain_name == 'vk':
            return Vk(source)
        elif domain_name == 'discord':
            pass
        elif domain_name == 'instagram':
            pass
        elif domain_name == 'tiktok':
            pass
    elif validators.email(source):
        pass
    raise exceptions.UnexpectedSource(
        'The link format is not supported or an unavailable link is specified.')


def get_random_card():
    try:
        return random.choice(list(game.sources)).get_random_card()
    except exceptions.NoAnyPosts:
        return get_random_card()
