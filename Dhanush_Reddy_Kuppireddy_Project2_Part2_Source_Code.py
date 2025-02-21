import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set
import os
import time

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_heading(text: str):
    """Print a formatted heading"""
    print("\n" + "=" * 50)
    print(text.center(50))
    print("=" * 50 + "\n")

def get_user_input(prompt: str, valid_options: List[str]) -> str:
    """Get and validate user input"""
    while True:
        print(f"\n{prompt}")
        choice = input("> ").strip().upper()
        if choice in [opt.upper() for opt in valid_options]:
            return choice
        print(f"Invalid choice. Please choose from: {', '.join(valid_options)}")

@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

class Room:
    def __init__(self, name: str, positions: List[Position]):
        self.name = name
        self.positions = positions
        self.connected_rooms = []
        self.entry_points = positions

    def add_connection(self, room: 'Room'):
        if room not in self.connected_rooms:
            self.connected_rooms.append(room)
            room.connected_rooms.append(self)

    def __str__(self):
        return self.name

class Card:
    def __init__(self, name: str, card_type: str):
        self.name = name
        self.card_type = card_type  # 'character', 'weapon', or 'room'

    def __str__(self):
        return f"{self.name} ({self.card_type})"

class Character:
    def __init__(self, name: str, starting_position: Position):
        self.name = name
        self.position = starting_position
        self.current_room = None

    def move_to(self, new_position: Position, new_room: Optional[Room] = None):
        self.position = new_position
        self.current_room = new_room

class Weapon:
    def __init__(self, name: str):
        self.name = name
        self.current_room = None

class Player:
    def __init__(self, character: Character, is_human: bool = False):
        self.character = character
        self.cards: List[Card] = []
        self.notes: Set[str] = set()
        self.is_eliminated = False
        self.is_human = is_human

    def add_card(self, card: Card):
        self.cards.append(card)

    def can_refute(self, suggestion: Tuple[str, str, str]) -> Optional[Card]:
        """Check if player can refute a suggestion with one of their cards"""
        suggested_cards = [
            card for card in self.cards 
            if card.name in suggestion
        ]
        return suggested_cards[0] if suggested_cards else None

    def get_valid_moves(self, game: 'CluedoGame') -> List[Tuple[Position, Optional[Room]]]:
        """Get valid moves for the player"""
        valid_moves = []
        current_pos = self.character.position
        
        # Add connected rooms if in a room
        if self.character.current_room:
            for room in self.character.current_room.connected_rooms:
                for pos in room.entry_points:
                    valid_moves.append((pos, room))
        
        # Add adjacent positions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = current_pos.x + dx
            new_y = current_pos.y + dy
            if 0 <= new_x <= 2 and 0 <= new_y <= 5:
                new_pos = Position(new_x, new_y)
                room = None
                for r in game.rooms.values():
                    if new_pos in r.positions:
                        room = r
                        break
                valid_moves.append((new_pos, room))
        
        return valid_moves

    def make_move(self, game: 'CluedoGame'):
        """Handle player movement"""
        valid_moves = self.get_valid_moves(game)
        
        if self.is_human:
            print("\nAvailable moves:")
            for i, (pos, room) in enumerate(valid_moves):
                location = f"Room: {room.name}" if room else f"Position: ({pos.x}, {pos.y})"
                print(f"{i+1}. Move to {location}")
            
            choice = int(get_user_input(
                "Choose your move (enter number):",
                [str(i+1) for i in range(len(valid_moves))]
            )) - 1
            
            new_pos, new_room = valid_moves[choice]
        else:
            new_pos, new_room = random.choice(valid_moves)
        
        self.character.move_to(new_pos, new_room)
        return new_room

    def make_suggestion(self, game: 'CluedoGame', current_room: Room) -> Optional[Tuple[str, str, str]]:
        """Make a suggestion about the crime"""
        if self.is_human:
            print("\nMake a suggestion:")
            print(f"Current room: {current_room.name}")
            
            # Choose suspect
            print("\nChoose a suspect:")
            suspects = [char.name for char in game.characters]
            for i, suspect in enumerate(suspects):
                print(f"{i+1}. {suspect}")
            suspect_idx = int(get_user_input(
                "Enter suspect number:",
                [str(i+1) for i in range(len(suspects))]
            )) - 1
            
            # Choose weapon
            print("\nChoose a weapon:")
            weapons = [weapon.name for weapon in game.weapons]
            for i, weapon in enumerate(weapons):
                print(f"{i+1}. {weapon}")
            weapon_idx = int(get_user_input(
                "Enter weapon number:",
                [str(i+1) for i in range(len(weapons))]
            )) - 1
            
            return (suspects[suspect_idx], weapons[weapon_idx], current_room.name)
        else:
            return (
                random.choice([char.name for char in game.characters]),
                random.choice([weapon.name for weapon in game.weapons]),
                current_room.name
            )

    def make_accusation(self, game: 'CluedoGame') -> Optional[Tuple[str, str, str]]:
        """Make a final accusation"""
        if self.is_human:
            print("\nMake your accusation:")
            make_it = get_user_input(
                "Are you sure you want to make an accusation? (Y/N)",
                ["Y", "N"]
            )
            
            if make_it == "N":
                return None
                
            # Choose suspect
            print("\nChoose the murderer:")
            suspects = [char.name for char in game.characters]
            for i, suspect in enumerate(suspects):
                print(f"{i+1}. {suspect}")
            suspect_idx = int(get_user_input(
                "Enter suspect number:",
                [str(i+1) for i in range(len(suspects))]
            )) - 1
            
            # Choose weapon
            print("\nChoose the murder weapon:")
            weapons = [weapon.name for weapon in game.weapons]
            for i, weapon in enumerate(weapons):
                print(f"{i+1}. {weapon}")
            weapon_idx = int(get_user_input(
                "Enter weapon number:",
                [str(i+1) for i in range(len(weapons))]
            )) - 1
            
            # Choose room
            print("\nChoose the murder room:")
            rooms = list(game.rooms.keys())
            for i, room in enumerate(rooms):
                print(f"{i+1}. {room}")
            room_idx = int(get_user_input(
                "Enter room number:",
                [str(i+1) for i in range(len(rooms))]
            )) - 1
            
            return (suspects[suspect_idx], weapons[weapon_idx], rooms[room_idx])
        else:
            if random.random() < 0.1:  # 10% chance for AI to make accusation
                return (
                    random.choice([char.name for char in game.characters]),
                    random.choice([weapon.name for weapon in game.weapons]),
                    random.choice(list(game.rooms.keys()))
                )
            return None

class CluedoGame:
    def __init__(self, num_human_players: int = 1):
        self.rooms = self._initialize_rooms()
        self.characters = self._initialize_characters()
        self.weapons = self._initialize_weapons()
        self.solution = self._select_solution()
        self._distribute_weapons_to_rooms()
        
        self.players: List[Player] = []
        self.current_player_index = 0
        self.game_over = False
        self.winner = None
        
        self._setup_cards_and_players(num_human_players)

    def _initialize_rooms(self) -> Dict[str, Room]:
        room_positions = {
            "Kitchen": [Position(0, 0), Position(0, 1)],
            "Ballroom": [Position(1, 0), Position(1, 1)],
            "Conservatory": [Position(2, 0), Position(2, 1)],
            "Dining Room": [Position(0, 2), Position(0, 3)],
            "Library": [Position(1, 2), Position(1, 3)],
            "Study": [Position(2, 2), Position(2, 3)],
            "Hall": [Position(0, 4), Position(0, 5)],
            "Lounge": [Position(1, 4), Position(1, 5)],
            "Billiard Room": [Position(2, 4), Position(2, 5)]
        }
        
        rooms = {name: Room(name, positions) for name, positions in room_positions.items()}
        
        # Define room connections
        connections = [
            ("Kitchen", "Ballroom"),
            ("Ballroom", "Conservatory"),
            ("Dining Room", "Library"),
            ("Library", "Study"),
            ("Hall", "Lounge"),
            ("Lounge", "Billiard Room")
        ]
        
        for room1_name, room2_name in connections:
            rooms[room1_name].add_connection(rooms[room2_name])
        
        return rooms

    def _initialize_characters(self) -> List[Character]:
        character_starts = {
            "Miss Scarlett": Position(0, 0),
            "Colonel Mustard": Position(1, 0),
            "Mrs. White": Position(2, 0),
            "Reverend Green": Position(0, 5),
            "Mrs. Peacock": Position(1, 5),
            "Professor Plum": Position(2, 5)
        }
        
        characters = []
        for name, position in character_starts.items():
            character = Character(name, position)
            for room in self.rooms.values():
                if position in room.positions:
                    character.current_room = room
                    break
            characters.append(character)
        return characters

    def _initialize_weapons(self) -> List[Weapon]:
        weapon_names = [
            "Candlestick",
            "Dagger",
            "Lead Pipe",
            "Revolver",
            "Rope",
            "Wrench"
        ]
        return [Weapon(name) for name in weapon_names]

    def _select_solution(self) -> Tuple[Character, Weapon, Room]:
        murderer = random.choice(self.characters)
        weapon = random.choice(self.weapons)
        room = random.choice(list(self.rooms.values()))
        return (murderer, weapon, room)

    def _distribute_weapons_to_rooms(self):
        available_rooms = list(self.rooms.values())
        for weapon in self.weapons:
            if weapon != self.solution[1]:
                room = random.choice(available_rooms)
                weapon.current_room = room

    def _setup_cards_and_players(self, num_human_players: int):
        character_cards = [Card(char.name, 'character') for char in self.characters]
        weapon_cards = [Card(weapon.name, 'weapon') for weapon in self.weapons]
        room_cards = [Card(room.name, 'room') for room in self.rooms.values()]

        all_cards = character_cards + weapon_cards + room_cards
        solution_cards = [
            card for card in all_cards 
            if card.name in [self.solution[0].name, self.solution[1].name, self.solution[2].name]
        ]
        for card in solution_cards:
            all_cards.remove(card)

        # Create players
        for i, character in enumerate(self.characters):
            is_human = i < num_human_players
            player = Player(character, is_human)
            self.players.append(player)

        # Distribute remaining cards
        random.shuffle(all_cards)
        for i, card in enumerate(all_cards):
            player_index = i % len(self.players)
            self.players[player_index].add_card(card)

    def handle_suggestion(self, suggesting_player: Player, suggestion: Tuple[str, str, str]) -> Optional[Card]:
        if suggesting_player.is_human:
            print(f"\n{suggesting_player.character.name} suggests:")
            print(f"Murderer: {suggestion[0]}")
            print(f"Weapon: {suggestion[1]}")
            print(f"Room: {suggestion[2]}")

        start_idx = (self.players.index(suggesting_player) + 1) % len(self.players)
        current_idx = start_idx

        while current_idx != self.players.index(suggesting_player):
            player = self.players[current_idx]
            if not player.is_eliminated:
                refutation = player.can_refute(suggestion)
                if refutation:
                    if suggesting_player.is_human:
                        print(f"\n{player.character.name} refuted with {refutation}")
                    suggesting_player.notes.add(f"Suggestion {suggestion} refuted with {refutation}")
                    return refutation
            current_idx = (current_idx + 1) % len(self.players)

        if suggesting_player.is_human:
            print("\nNo one could refute the suggestion!")
        suggesting_player.notes.add(f"Suggestion {suggestion} not refuted")
        return None

    def handle_accusation(self, player: Player, accusation: Tuple[str, str, str]) -> bool:
        correct_accusation = (
            accusation[0] == self.solution[0].name and
            accusation[1] == self.solution[1].name and
            accusation[2] == self.solution[2].name
        )

        if correct_accusation:
            self.game_over = True
            self.winner = player
            return True
        else:
            player.is_eliminated = True
            active_players = [p for p in self.players if not p.is_eliminated]
            if len(active_players) == 1:
                self.game_over = True
                self.winner = active_players[0]
            return False
        
    def print_player_state(self, player: Player):
        """Print the current state for a human player"""
        print(f"\nYour Cards:")
        for card in player.cards:
            print(f"- {card}")
        
        print("\nYour Notes:")
        for note in player.notes:
            print(f"- {note}")

    def print_game_state(self):
        """Print the current state of the game"""
        print("\n=== CLUEDO GAME STATE ===")
        
        print("\nPlayers and their cards:")
        for player in self.players:
            if player.is_eliminated:
                status = "ELIMINATED"
            else:
                status = "Active"
            print(f"\n{player.character.name} ({status}):")
            if player.is_human:
                print("Cards:", ", ".join(str(card) for card in player.cards))
            if player.notes:
                print("Notes:", "\n  ".join(player.notes))

        print("\nRooms and their connections:")
        for room_name, room in self.rooms.items():
            connected_rooms = [r.name for r in room.connected_rooms]
            print(f"{room_name} - Connected to: {', '.join(connected_rooms)}")

        print("\nCharacters and their locations:")
        for character in self.characters:
            location = character.current_room.name if character.current_room else "Hallway"
            print(f"{character.name} is in {location} at position ({character.position.x}, {character.position.y})")

        print("\nWeapons and their locations:")
        for weapon in self.weapons:
            location = weapon.current_room.name if weapon.current_room else "Unknown"
            print(f"{weapon.name} is in {location}")

def main():
    clear_screen()
    print_heading("Welcome to Cluedo!")
    
    # Get number of human players
    num_players = int(get_user_input(
        "How many human players? (1-6):",
        ["1", "2", "3", "4", "5", "6"]
    ))
    
    # Initialize game
    game = CluedoGame(num_human_players=num_players)
    
    print("\nGame initialized with:")
    print("- 9 rooms")
    print("- 6 characters")
    print("- 6 weapons")
    print("\nCards have been distributed and a murder solution has been selected.")
    time.sleep(2)
    
    # Main game loop
    round_number = 1
    while not game.game_over and round_number <= 20:  # Extended to 20 rounds
        clear_screen()
        print_heading(f"Round {round_number}")
        
        for player in game.players:
            if game.game_over:
                break
                
            if player.is_eliminated:
                continue
                
            clear_screen()
            print_heading(f"{player.character.name}'s Turn")
            print("Status: " + ("Human Player" if player.is_human else "Computer Player"))
            
            if player.is_human:
                game.print_player_state(player)
                input("\nPress Enter to start your turn...")
            
            # 1. Movement
            new_room = player.make_move(game)
            
            # 2. Make suggestion if in a room
            if new_room:
                if player.is_human:
                    print(f"\nYou are in the {new_room.name}.")
                    make_suggestion = get_user_input(
                        "Would you like to make a suggestion? (Y/N)",
                        ["Y", "N"]
                    )
                    if make_suggestion == "Y":
                        suggestion = player.make_suggestion(game, new_room)
                        refutation = game.handle_suggestion(player, suggestion)
                        if refutation:
                            print(f"\nSuggestion was refuted with: {refutation}")
                        else:
                            print("\nNo one could refute your suggestion!")
                        input("\nPress Enter to continue...")
                else:
                    suggestion = player.make_suggestion(game, new_room)
                    game.handle_suggestion(player, suggestion)
            
            # 3. Make accusation
            if player.is_human:
                accusation = player.make_accusation(game)
                if accusation:
                    success = game.handle_accusation(player, accusation)
                    if success:
                        print(f"\n{player.character.name} won with correct accusation!")
                    else:
                        print(f"\n{player.character.name} made wrong accusation and is eliminated!")
                    input("\nPress Enter to continue...")
            else:
                accusation = player.make_accusation(game)
                if accusation:
                    game.handle_accusation(player, accusation)
        
        round_number += 1
        
        if round_number % 3 == 0:  # Show game state every 3 rounds
            clear_screen()
            game.print_game_state()
            input("\nPress Enter to continue...")
    
    # Game end
    clear_screen()
    print_heading("Game Over!")
    
    if game.winner:
        print(f"\n{game.winner.character.name} wins!")
    else:
        print("\nNo winner determined.")
    
    print("\n[DEBUG] The solution was:")
    print(f"Murderer: {game.solution[0].name}")
    print(f"Weapon: {game.solution[1].name}")
    print(f"Room: {game.solution[2].name}")

if __name__ == "__main__":
    main()
    