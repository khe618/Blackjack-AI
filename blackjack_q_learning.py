import random
from enum import Enum
class Moves(Enum):
    HIT = 1
    STAND = 2
    DOUBLE_DOWN = 3
class Policy:
    def __init__(self):
        self.hit_ev = 0
        self.stand_ev = 0
        self.dd_ev = 0
        self.hit_n = 0
        self.stand_n = 0
        self.dd_n = 0
    def update_ev(self, move, reward):
        if move == Moves.HIT:
            self.hit_ev += 0.01 * (reward - self.hit_ev)
            self.hit_n += 1
        elif move == Moves.STAND:
            self.stand_ev += 0.01 * (reward - self.stand_ev)
            self.stand_n += 1
        elif move == Moves.DOUBLE_DOWN:
            self.dd_ev += 0.01 * (2 * reward - self.dd_ev)
            self.dd_n += 1
    def determine_move(self):
        options =  [(Moves.HIT, self.hit_ev), (Moves.STAND, self.stand_ev), (Moves.DOUBLE_DOWN, self.dd_ev)]
        options.sort(key = lambda x: x[1], reverse = True)
        return options[0][0]
    def explore_move(self):
        options = [Moves.HIT, Moves.STAND, Moves.DOUBLE_DOWN]
        cum_prbs = [10 ** self.hit_ev]
        cum_prbs.append( (10 ** self.stand_ev) + cum_prbs[0])
        cum_prbs.append( (10 ** self.dd_ev) + cum_prbs[1])
        rand = random.uniform(0, cum_prbs[2])
        if rand < cum_prbs[0]:
            return options[0]
        if rand < cum_prbs[1]:
            return options[1]
        return options[2]
    def max_q(self):
        return max(self.hit_ev, self.stand_ev, self.dd_ev)
cards = [2,3,4,5,6,7,8,9,10,10,10,10,11] * 4
states = [ [ [Policy(), Policy()] for i in range(10) ] for j in range(17) ]
#states[i][j][k]:
#i = sum of your score (4-20 inclusive) - 4
#j = dealer's face up card value - 2
#k = 0 for unusable ace, 1 for usable ace
def simulate_game(explore = False):
    random.shuffle(cards)
    face_up = cards[0]
    hole_card = cards[1]
    dealers_cards = [face_up, hole_card]
    my_cards = [cards[2], cards[3]]
    card_count = 4
    usable_ace = 11 in my_cards
    move_arr = []
    policy_arr = []
    last_policy = None
    if sum(dealers_cards) == 21 or sum(my_cards) == 21:
        return
    while True:
        if sum(my_cards) >= 21:
            if sum(my_cards) > 21 and usable_ace:
                my_cards[my_cards.index(11)] = 1
                usable_ace = 11 in my_cards
            else:
                break
        try:
            next_policy = states[sum(my_cards) - 4][face_up - 2][int(usable_ace)]
        except IndexError:
            print([my_cards, face_up, usable_ace])
        if explore:
            next_move = next_policy.explore_move()
        else:
            next_move = next_policy.determine_move()
        move_arr.append(next_move)
        policy_arr.append(next_policy)
        if last_policy:
            last_policy[0].update_ev(last_policy[1], next_policy.max_q())
        last_policy = (next_policy, next_move)
        if next_move == Moves.HIT:
            my_cards.append(cards[card_count])
            card_count += 1
            usable_ace = 11 in my_cards
        elif next_move == Moves.DOUBLE_DOWN:
            my_cards.append(cards[card_count])
            card_count += 1
            usable_ace = 11 in my_cards
            if sum(my_cards) > 21 and usable_ace:
                my_cards[my_cards.index(11)] = 1
                usable_ace = 11 in my_cards
            break
        else:
            break
    while sum(dealers_cards) < 17 or sum(dealers_cards) == 17 and 11 in dealers_cards:
        dealers_cards.append(cards[card_count])
        card_count += 1
        if sum(dealers_cards) > 21 and 11 in dealers_cards:
            dealers_cards[dealers_cards.index(11)] = 1
    if sum(my_cards) > 21 or (sum(dealers_cards) <= 21 and sum(dealers_cards) > sum(my_cards)):
        last_policy[0].update_ev(last_policy[1], -1)
    elif sum(my_cards) > sum(dealers_cards) or sum(dealers_cards) > 21:
        last_policy[0].update_ev(last_policy[1], 1)
    else:
        last_policy[0].update_ev(last_policy[1], 0)
    return [dealers_cards, my_cards, move_arr, policy_arr]        
    
