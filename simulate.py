#!/usr/bin/env python3
import random

BASIC_STRATEGY = {
    "hard": {
        (17, 2): "stand", (17, 3): "stand", (17, 4): "stand", (17, 5): "stand", (17, 6): "stand",
        (17, 7): "stand", (17, 8): "stand", (17, 9): "stand", (17, 10): "stand", (17, 11): "stand",
        (16, 2): "stand", (16, 3): "stand", (16, 4): "stand", (16, 5): "stand", (16, 6): "stand",
        (16, 7): "hit", (16, 8): "hit", (16, 9): "hit", (16, 10): "hit", (16, 11): "hit",
        (15, 2): "stand", (15, 3): "stand", (15, 4): "stand", (15, 5): "stand", (15, 6): "stand",
        (15, 7): "hit", (15, 8): "hit", (15, 9): "hit", (15, 10): "hit", (15, 11): "hit",
        (14, 2): "stand", (14, 3): "stand", (14, 4): "stand", (14, 5): "stand", (14, 6): "stand",
        (14, 7): "hit", (14, 8): "hit", (14, 9): "hit", (14, 10): "hit", (14, 11): "hit",
        (13, 2): "stand", (13, 3): "stand", (13, 4): "stand", (13, 5): "stand", (13, 6): "stand",
        (13, 7): "hit", (13, 8): "hit", (13, 9): "hit", (13, 10): "hit", (13, 11): "hit",
        (12, 2): "hit", (12, 3): "hit", (12, 4): "stand", (12, 5): "stand", (12, 6): "stand",
        (12, 7): "hit", (12, 8): "hit", (12, 9): "hit", (12, 10): "hit", (12, 11): "hit",
    },
    "soft": {
        (19, 2): "stand", (19, 3): "stand", (19, 4): "stand", (19, 5): "stand", (19, 6): "stand",
        (19, 7): "stand", (19, 8): "stand", (19, 9): "stand", (19, 10): "stand", (19, 11): "stand",
        (18, 2): "stand", (18, 3): "stand", (18, 4): "stand", (18, 5): "double", (18, 6): "double",
        (18, 7): "stand", (18, 8): "stand", (18, 9): "hit", (18, 10): "hit", (18, 11): "hit",
        (17, 2): "hit", (17, 3): "hit", (17, 4): "hit", (17, 5): "hit", (17, 6): "hit",
        (17, 7): "hit", (17, 8): "hit", (17, 9): "hit", (17, 10): "hit", (17, 11): "hit",
    }
}


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = self.determine_color()
        self.value = self.determine_value()

    def determine_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def determine_color(self):
        if self.suit in ['hearts', 'diamonds']:
            return 'red'
        else:
            return 'black'

    def __repr__(self):
        return f"{self.rank}"


class Deck:
    def __init__(self):
        self.cards = self.create_deck()

    def create_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        return [Card(rank, suit) for suit in suits for rank in ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None


class Shoe:
    def __init__(self, num_decks=6, reshuffle_threshold=0.25):
        self.num_decks = num_decks
        self.reshuffle_threshold = reshuffle_threshold
        self.cards = self.create_shoe()
        self.shuffle()

    def create_shoe(self):
        return [card for _ in range(self.num_decks) for card in Deck().cards]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if len(self.cards) == 0:
            print("The shoe is empty. Reshuffling...")
            self.cards = self.create_shoe()
            self.shuffle()
        elif len(self.cards) <= self.reshuffle_threshold * self.num_decks * 52:
            print("Reshuffling the shoe as it is running low.")
            self.shuffle()
        return self.cards.pop()


class Player:
    def __init__(self, name, bankroll=1000):
        self.name = name
        self.bankroll = bankroll
        self.hand = []
        self.bet = 0

    def place_bet(self, amount):
        if amount > self.bankroll:
            raise ValueError("Insufficient funds to place bet.")
        self.bet = amount
        self.bankroll -= amount

    def receive_card(self, card):
        self.hand.append(card)

    def clear_hand(self):
        self.hand = []

    def calculate_hand_value(self):
        value = sum(card.value for card in self.hand)
        num_aces = sum(1 for card in self.hand if card.rank == 'A')
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def is_busted(self):
        return self.calculate_hand_value() > 21

    def __repr__(self):
        hand_str = ', '.join(str(card) for card in self.hand)
        return f"{self.name}: {hand_str} (Value: {self.calculate_hand_value()})"


class Dealer(Player):
    def __init__(self):
        super().__init__(name="Dealer")

    def should_hit(self):
        hand_value = self.calculate_hand_value()
        has_soft_17 = any(card.rank == 'A' for card in self.hand) and hand_value == 17
        return hand_value < 17 or has_soft_17


class BlackjackGame:
    def __init__(self, num_players=1, num_decks=6, reshuffle_threshold=0.25):
        self.num_players = num_players
        self.players = [Player(name=f"Player {i+1}") for i in range(num_players)]
        self.dealer = Dealer()
        self.shoe = Shoe(num_decks=num_decks, reshuffle_threshold=reshuffle_threshold)
        self.statistics = {"rounds": 0, "wins": 0, "losses": 0, "pushes": 0}

    def deal_initial_hands(self):
        cards_needed = 2 * (self.num_players + 1)  # Two cards for each player and the dealer
        if len(self.shoe.cards) < cards_needed:
            print("Not enough cards for a new round. Reshuffling...")
            self.shoe.cards = self.shoe.create_shoe()
            self.shoe.shuffle()

        for _ in range(2):
            for player in self.players:
                player.receive_card(self.shoe.draw_card())
            self.dealer.receive_card(self.shoe.draw_card())

    def player_turn(self, player):
        print(f"\n{player.name}'s turn:")
        while not player.is_busted():
            print(player)
            dealer_up_card = self.dealer.hand[0]
            action = self.get_strategy_action(player, dealer_up_card)
            print(f"{player.name} chooses to {action}.")
            if action == "hit":
                player.receive_card(self.shoe.draw_card())
            elif action == "stand":
                break
            elif action == "double":
                player.receive_card(self.shoe.draw_card())
                break
        print(f"{player.name} ends their turn.\n")

    def dealer_turn(self):
        print("\nDealer's turn:")
        while self.dealer.should_hit():
            print(self.dealer)
            self.dealer.receive_card(self.shoe.draw_card())
        print(f"Dealer ends their turn with:\n{self.dealer}\n")

    def resolve_hands(self):
        dealer_value = self.dealer.calculate_hand_value()
        for player in self.players:
            player_value = player.calculate_hand_value()
            if player.is_busted():
                print(f"{player.name} busted! Dealer wins.")
                self.statistics["losses"] += 1
            elif dealer_value > 21 or player_value > dealer_value:
                print(f"{player.name} wins!")
                self.statistics["wins"] += 1
            elif player_value == dealer_value:
                print(f"{player.name} pushes.")
                self.statistics["pushes"] += 1
            else:
                print(f"{player.name} loses.")
                self.statistics["losses"] += 1

    def reset_hands(self):
        for player in self.players:
            player.clear_hand()
        self.dealer.clear_hand()

    def play_round(self):
        self.deal_initial_hands()
        for player in self.players:
            self.player_turn(player)
        self.dealer_turn()
        self.resolve_hands()
        self.reset_hands()

    def get_strategy_action(self, player, dealer_up_card):
        """Get the optimal action for the player based on the strategy dictionary."""
        hand_value = player.calculate_hand_value()
        has_ace = any(card.rank == 'A' for card in player.hand)
        is_soft = has_ace and hand_value <= 21
        dealer_value = dealer_up_card.value

        # Soft totals
        if is_soft:
            return BASIC_STRATEGY["soft"].get((hand_value, dealer_value), "hit")

        # Hard totals
        return BASIC_STRATEGY["hard"].get((hand_value, dealer_value), "hit")

    def player_turn(self, player):
        """Automate the player's turn using the strategy dictionary."""
        print(f"\n{player.name}'s turn:")
        while not player.is_busted():
            print(player)
            dealer_up_card = self.dealer.hand[0]  # Dealer's visible card
            action = self.get_strategy_action(player, dealer_up_card)
            print(f"{player.name} chooses to {action}.")
            if action == "hit":
                player.receive_card(self.shoe.draw_card())
            elif action == "stand":
                break
            elif action == "double":
                player.receive_card(self.shoe.draw_card())
                break  # Double ends the turn
        print(f"{player.name} ends their turn.\n")

    def simulate(self, num_rounds):
        for _ in range(num_rounds):
            self.statistics["rounds"] += 1
            self.play_round()

        print("\nSimulation Results:")
        print(f"Total Rounds: {self.statistics['rounds']}")
        print(f"Wins: {self.statistics['wins']}")
        print(f"Losses: {self.statistics['losses']}")
        print(f"Pushes: {self.statistics['pushes']}")


if __name__ == "__main__":
    game = BlackjackGame(num_players=1, num_decks=6)

    print("Simulating 100 rounds...")
    game.simulate(100)
    print("Simulation completed.")
