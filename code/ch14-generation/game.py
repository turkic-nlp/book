"""Bounded game controller. Callbacks supply models, rules and guess policy.

check_clue returns valid/invalid/review. Only an adjudicated valid clue reaches
 the guesser. The guesser receives no target or forbidden list in its context.
"""
from copy import deepcopy


def play(target, forbidden, describe, guess, check_clue, matches, rounds=3):
    if rounds < 1 or not target.strip() or not forbidden:
        raise ValueError('target, forbidden lemmas and a positive round limit required')
    describer = [{'role': 'system', 'content':
        f'Describe {target} without using these lemmas or their inflections: {forbidden}.'}]
    guesser = [{'role': 'system', 'content': 'Guess the word from the clues.'}]
    turns = []
    for number in range(1, rounds + 1):
        clue = describe(deepcopy(describer))
        if not isinstance(clue, str) or not clue.strip():
            return {'outcome': 'empty_clue', 'turns': turns}
        status = check_clue(clue)
        if status not in {'valid', 'invalid', 'review'}:
            raise ValueError('check_clue must return valid, invalid or review')
        turn = {'round': number, 'clue': clue, 'rule_status': status}
        turns.append(turn)
        if status != 'valid':
            return {'outcome': status, 'turns': turns}
        describer.append({'role': 'assistant', 'content': clue})
        guesser.append({'role': 'user', 'content': clue})
        answer = guess(deepcopy(guesser))
        if not isinstance(answer, str) or not answer.strip():
            return {'outcome': 'empty_guess', 'turns': turns}
        turn['guess'] = answer
        if matches(answer, target):
            return {'outcome': 'success', 'turns': turns}
        guesser.append({'role': 'assistant', 'content': answer})
        describer.append({'role': 'user', 'content': f'The guess was {answer}. Give another clue.'})
    return {'outcome': 'turn_limit', 'turns': turns}
