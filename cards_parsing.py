import math
import random

import validators
import vk_api

import game_configuration
import game_exceptions
import game_rules

vk_requests = vk_api.VkApi(token=game_configuration.VK_TOKEN).get_api()


class Link:
    def __init__(self, link):
        self.link = link


class Source:
    pass


class Vk(Source):
    def __init__(self, link):
        self.link = link
        self.domain = link[link.rfind(r'/') + 1:]
        game_rules.included_types = {y for i in game_rules.included_types if (y := Vk.types.get(i))}
        game_rules.excluded_types = {y for i in game_rules.excluded_types if (y := Vk.types.get(i))}

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
            raise game_exceptions.NoAnyPosts

        try:
            attachments = vk_requests.wall.get(domain=self.domain,
                                               offset=random.randrange(self.cards_num),
                                               count=1)['items'][0]['attachments']
        except KeyError:
            return self.get_random_card()

        # If attachments are found, then get the random one
        random.shuffle(attachments)
        for attachment in attachments:
            if attachment['type'] not in game_rules.excluded_types:
                if game_rules.included_types:
                    if attachment['type'] not in game_rules.included_types:
                        continue
                return extract_content_from_attachment(attachment)

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
    raise game_exceptions.Unexpectedsource('The link format is not supported or an unavailable link is specified.')
