from typing import Collection

include_used_cards: bool = False
step_timeout: float = 60
"""The time in seconds that the player has to make a choice."""
cards_per_player: int = 6
winning_score: float = 3
included_types: Collection[str] = ('photo',)
excluded_types: Collection[str] = ()
card_receiving_timeout: float = 5
"""The time in seconds for which the card can be received."""
