import random


class PhraseSender:

    def __init__(self, identificator, maintainer_username):
        self.uniq_id = identificator
        self.maintainer_username = maintainer_username
        self.participants = []
        self.is_game_started = False
        self.group_number = 0

    def get_random_participant(self, parts):
        index = random.randrange(0, len(parts))
        participant = parts[index]
        parts.remove(parts[index])
        return participant

    def get_correct_group_number(self, phrase_number):
        while len(self.participants) > phrase_number * self.group_number:
            phrase_number += 1
        return self.group_number

    def give_phrases(self, all_phrases, bot):
        p = self.participants.copy()
        ph = all_phrases.copy()
        index = len(p)
        while index > 0:
            parts_group = []
            step = self.get_correct_group_number(len(all_phrases))
            if len(p) < self.group_number:
                step = len(p)
            for i in range(step):
                parts_group.append(self.get_random_participant(p))
            rp = random.randrange(0, len(ph))
            phrase = ph[rp]
            ph.remove(ph[rp])
            index -= step
            for i in parts_group:
                bot.send_message(i, phrase)

    def add_participant(self, participant):
        self.participants.append(participant)

    def get_correct_ending(self):
        o = len(self.participants) % 10
        if o == 1:
            return ' участник'
        elif o == 2 or o == 3 or o == 4:
            return ' участника'
        else:
            return ' участников'