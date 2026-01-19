from .board import Board
from .enums import GameMode
from .enums import Player
from .enums import CellType
from .enums import CellState
import pygame
import math

class Atoll:
    def __init__(self, board_size, first_player, game_mode):
        self.board = Board(board_size)
        self.game_mode = game_mode
        self.current_player = first_player
        self.last_move = None
        self.board_logic = {}

        self.game_over = False #dodato cuvanje pobednika i info o tome da li je igra zavrsena, u odnosu na to moze da se napravi popup
        self.winner = None
        self.black_islands = [] #dodato cuvanje ostrva, tj polja koja cuvaju ostrva
        self.white_islands = []
        self.all_islands = []

        self.intialize_board_logic()
        self.identify_islands() #zovemo funkciju za identifikaciju ostrva da bi se proveravao kraj igre lakse

    def draw_board(self, screen):
        self.board.draw_board(screen)

    #def intialize_board_logic(self):
    #    for i in range(0, 2*self.board.size):
    #        for j in range(0,2*self.board.size):
    #            alphabetic_coordinate = chr(ord("A") + i)
    #            numeric_coordinate = j + 1
    #            self.board_logic[(alphabetic_coordinate,numeric_coordinate)] = CellState.EMPTY

#izmenjeno u fazi 2 tako da identifikuje ostrva koristeci prepoznavanje nacrtanih crnih i belih polja i zvanje identifikatora ostrva

    def intialize_board_logic(self):
        self.board_logic = {}

        for i in range(self.board.board_size):
            for j in range(self.board.board_size):
                cell_data = self.board.board[i][j]

                if cell_data.cell_type in [CellType.EMPTY, CellType.BLACK, CellType.WHITE]:
                    coord = self.convert_coordinates(i, j)
                
                    if cell_data.cell_type == CellType.BLACK:
                        self.board_logic[coord] = CellState.BLACK
                    elif cell_data.cell_type == CellType.WHITE:
                        self.board_logic[coord] = CellState.WHITE
                    else:
                        self.board_logic[coord] = CellState.EMPTY
    
        self.identify_islands()

#radna verzija funkcije za indeksiranje ostrva, na kraju je ubacena samo u okviru identify_islands bez poziva
    #def get_island_id(self, r, c):
    #    size = float(self.board.board_size)
    #    center = (size - 1) / 2.0
    #    angle = math.degrees(math.atan2(float(r) - center, float(c) - center))
    #    print(angle)
    #    if angle < 0:
    #        angle += 360
    #    island_id = int(((angle + 15) % 360) / 30)
    #    return island_id % 12

#dodato u fazi 2, najkomplikovanija funkcija ovde verovatno - pre svega jer treba kroz nju idovati sva ostrva sa starta igre, sto je neophodno jer iako je 
#broj ostrva fiksan, cvorovi u ostrvima nisu, pa se pre svega radi prolazak kroz celu tablu i upisuje se koje je polje kako obojeno, a onda se
#radi indeksiranje ostrva koristeci math.atan2 da bismo nasli ugao svakog ostrva i da bismo ih sortirali i ubacili u odgovarajucu grupu ostrva
    def identify_islands(self):
        self.black_islands = []
        self.white_islands = []
        self.all_islands = []
        visited = set()

        found_islands_data = []

        for coord, state in self.board_logic.items():
            if state!= CellState.EMPTY and coord not in visited:
                current_island = set()
                queue = [coord]
                visited.add(coord)
                color = state
                while queue:
                    curr = queue.pop(0)
                    current_island.add(curr)
                    for neighbor in self.get_neighbors(curr):
                        if neighbor in self.board_logic and self.board_logic[neighbor] == color and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            #ovaj ceo deo se izvrsava zato sto na pocetku nam trebaju koja su polja iscrtana
                            #pri inicijalizaciji. na osnovu tih iscrtanih polja se radi dalje

                first_cell = list(current_island)[0]
                r, c = self.inverse_convert_coordinates(first_cell[0], first_cell[1])
                #za svako ostrvo na koje se naidje, trazimo ugao od centra. ovo se radi zato sto je neophodno da se ostrva indeksiraju
                #kako bismo mogli da kasnije poredimo indekse za racunanje kraja igre
                size = float(self.board.board_size)
                center = (size - 1) / 2.0
                angle = math.degrees(math.atan2(float(r) - center, float(c) - center))
                if angle < 0: angle += 360
                
                found_islands_data.append((angle, current_island,color))
                #zgodno da bude ovako jer nam za svako nadjeno ostrvo to treba da znamo kako da ga indeksiramo i u koju listu ostrva da ga ubacimo

        found_islands_data.sort()

        for angle, island, color in found_islands_data:
            self.all_islands.append(island)
            if color == CellState.BLACK:
                self.black_islands.append(island)
            else:
                self.white_islands.append(island) #u skladu sa uglom u odnosu na pocetak, dodajemo jedno po jedno ostrvo u svoje respectable grupe ostrva u odnosu na boju

#dodata provera kraja igre, provera da li je move legalan i da li je doslo do kraja igre, koju moze da prekine ako jeste. ima zakomentarisan deo za printovanje sortirane table
    def move(self, coordinates):
        if self.game_over:
            return False #prekida promenu igraca kada je igra gotova

        i, j = coordinates
        converted_coords = self.convert_coordinates(i,j)

        if self.board_logic.get(converted_coords) != CellState.EMPTY:
            return False #cisto da bi postojala provera da li je napravljena greska, iako niko ne moze da je napravi
        
        self.last_move = converted_coords
        self.board_logic[converted_coords] = CellState.WHITE if self.current_player == Player.WHITE else CellState.BLACK
        self.board.board[i][j].cell_type = CellType.WHITE if self.current_player == Player.WHITE else CellType.BLACK
        self.board.update_buttons()

        is_over, color = self.is_game_over()
        if is_over:
            self.game_over = True
            self.winner = "White" if color == Player.WHITE else "Black"
            print(f"Game over, winner is {self.winner}")
            return True
        
        #sorted_logic = dict(sorted(self.board_logic.items(), key=lambda item: (item[0][0], item[0][1])))
        #for coord, state in sorted_logic.items():
        #    print(f"{coord}: {state}")
        
        self.change_player()
        return True #jer imamo return False u ifu gore

    def draw_last_move(self,screen):
        if self.last_move!=None:
            alphabetic_coordinate, numeric_coordinate = self.last_move
            last_move = "Last move: black" if self.board_logic.get(self.last_move) == CellState.BLACK else "Last move: white"
            last_move = last_move + " (" + alphabetic_coordinate +", " + str(numeric_coordinate) + ")"

            font = pygame.font.Font(None, 28)
            text_surface = font.render(last_move, True, (0, 0, 0))
            screen.blit(text_surface, (700, 20))


    def undo(self):
        pass

    def change_player(self):
        self.current_player = Player.WHITE if self.current_player == Player.BLACK else Player.BLACK

    def check_hover(self, mouse_pos):
        self.board.check_hower(mouse_pos)

    def check_click(self, pos):
        return self.board.check_click(pos)

    def convert_coordinates(self, i, j):
        alphabetic_coordinate = chr(ord("A") + j//2 - 2)
        numeric_coordinate = 3 + 2*i - (self.board.size - (j//2 - 2+1))
        numeric_coordinate = (i - (self.board.size - (j//2-2+1)))//2
        return (alphabetic_coordinate,numeric_coordinate)
    
    def inverse_convert_coordinates(self, alphabetic_coordinate, numeric_coordinate):
        S = self.board.size
        j = 2 * (ord(alphabetic_coordinate) - ord("A") + 2)
        i = 2 * numeric_coordinate + S - (ord(alphabetic_coordinate) - ord("A"))
        return i, j

#stavka 2 na slajdu za funkcije koje implementiraju operator promene stanja igre, napravljeno tako da prodje kroz sva polja i vraca sva polja imaju state empty jer ta polja mogu da se odigraju
    def get_legal_moves(self, current_board_logic):
        return[coord for coord, state in current_board_logic.items() if state == CellState.EMPTY]

#stavka 1 na slajdu za funkcije koje implementiraju operator promene stanja igre, napravljeno tako da dobijamo stanje na osnovu simuliranog poteza
#kao rezultat ne dobijamo odigran potez, nego se move metoda koristi da se dobije simulacija poteza
    def get_next_state(self, current_board_logic, move, player_color):
        new_state = current_board_logic.copy()
        new_state[move] = player_color
        return new_state 

#stavka 3 na slajdu za funkcije koje implementiraju operator promene stanja igre, napravljeno tako da kombinuje stavku 1 i stavku 2 i da nam, za SVAKI simulirani potez, rezultat
    def get_all_possible_states(self, current_board_logic, player_color):
        possible_moves = self.get_legal_moves(current_board_logic)
        all_states = []

        for move in possible_moves:
            next_s = self.get_next_state(current_board_logic, move, player_color)
            all_states.append(next_s)
        return all_states

#neophodna metoda za pronalazenje komsija na osnovu postojece notacije koja se koristi, koristi se za id ostrva koja postoje na pocetku igre
#koristi se za pronalazenje puteva izmedju ostrva, tj za id kada su ostrva povezana mostom
#takodje ce se koristiti za AI da zna gde je pametno da se odigra najverovatnije
    def get_neighbors(self, coordinates):
        L, N = coordinates
        char_code = ord(L)
        potential_neighbors = [
            (L,N-1), (L,N +1),
            (chr(char_code-1), N-1), (chr(char_code - 1), N),
            (chr(char_code+1), N), (chr(char_code+1), N+1)
        ]
        return[c for c in potential_neighbors if c in self.board_logic]        

#metoda koja proverava da li je kraj igre, za igraca koji je upravo odigrao potez
    def is_game_over(self):
        color = CellState.BLACK if self.current_player == Player.BLACK else CellState.WHITE
        islands = self.black_islands if self.current_player == Player.BLACK else self.white_islands

        for i in range(len(islands)):
            for j in range(i+1, len(islands)):
                if self._has_path(islands[i], islands[j], color):
                    if (self.get_distances(islands[i], islands[j]) >= self.get_winning_treshold()):
                        return True, self.current_player
        return False, None

#zapravo sam BFS koji za svaka 2 ostrva proverava da li su spojena na osnovu neighbor polja
    def _has_path(self, start_island, target_island, color):
        queue = list(start_island)
        visited = set(start_island)
        while(queue):
            curr=queue.pop(0)
            if curr in target_island:
                return True
            for neighbor in self.get_neighbors(curr):
                if neighbor not in visited and self.board_logic.get(neighbor) == color:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False
    
    #racuna winning treshold, tj koliko ostrva je neophodno da se "osvoji" da bi igrac pobedio
    #treshold je uvek 7 jer je broj ostrva fiksan, 12, ali u slucaju da ima vise ostrva je funkcija korisna 
    def get_winning_treshold(self):
        total = len(self.white_islands) + len(self.black_islands)
        return (total//2)+1
    
    #metoda koja vraca najmanju od dve duzine izmedju pocetnog i krajnjeg spojenog ostrva, kada se racuna u smeru i suprotno od smera kazaljke na satu
    #radi tako sto broji indekse izmedju dva povezana ostrva, tj dva ostrva koja se posalju u funkciju i vraca manju razdaljinu
    def get_distances(self, isl_a, isl_b):
        idx_a = self.all_islands.index(isl_a)
        idx_b = self.all_islands.index(isl_b)
        n = len(self.all_islands)
        dist_1 = abs(idx_a - idx_b) + 1
        dist_2 = n - abs(idx_a - idx_b) + 1
        #print(dist_1, dist_2)
        return min(dist_1, dist_2)