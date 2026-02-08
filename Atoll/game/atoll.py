from .board import Board
from .enums import GameMode
from .enums import Player
from .enums import CellType
from .enums import CellState
import pygame
import math
import heapq
import random

class Atoll:
    def __init__(self, board_size, first_player, game_mode, computer_color):
        self.board = Board(board_size)
        self.game_mode = game_mode
        self.current_player = first_player
        self.computer_color = computer_color
        self.last_move = None
        self.board_logic = {}
        self.depth = 2

        self.game_over = False #dodato cuvanje pobednika i info o tome da li je igra zavrsena, u odnosu na to moze da se napravi popup
        self.winner = None
        self.black_islands = [] #dodato cuvanje ostrva, tj polja koja cuvaju ostrva
        self.white_islands = []
        self.all_islands = []

        self.intialize_board_logic()
        self.identify_islands() #zovemo funkciju za identifikaciju ostrva da bi se proveravao kraj igre lakse

        self.center_point = self.center_coord()
        self.distances_to_center = {}

        for coord in self.board_logic.keys():
            self.distances_to_center[coord] = self.distance(coord, self.center_point)

    def draw_board(self, screen):
        self.board.draw_board(screen)

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
                    for neighbor in self.get_neighbors(curr,self.board_logic):
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
#move sad vraca True/False ispravno
    def move(self, coordinates):
        if self.game_over:
            return True #prekida promenu igraca kada je igra gotova

        i, j = coordinates
        converted_coords = self.convert_coordinates(i,j)

        if self.board_logic.get(converted_coords) != CellState.EMPTY:
            return False #cisto da bi postojala provera da li je napravljena greska, iako niko ne moze da je napravi
        
        self.last_move = converted_coords
        self.board_logic[converted_coords] = CellState.WHITE if self.current_player == Player.WHITE else CellState.BLACK
        self.board.board[i][j].cell_type = CellType.WHITE if self.current_player == Player.WHITE else CellType.BLACK
        self.board.update_buttons()

        if self.is_game_over(self.board_logic, Player.BLACK):
            self.game_over = True
            self.winner = "Black"
            print(f"Game over, winner is {self.winner}")
            return True
        
        if self.is_game_over(self.board_logic, Player.WHITE):
            self.game_over = True
            self.winner = "White"
            print(f"Game over, winner is {self.winner}")
            return True
        
        #sorted_logic = dict(sorted(self.board_logic.items(), key=lambda item: (item[0][0], item[0][1])))
        #for coord, state in sorted_logic.items():
        #    print(f"{coord}: {state}")
        
        self.change_player()
        return False

    def draw_last_move(self,screen):
        if self.last_move!=None:
            alphabetic_coordinate, numeric_coordinate = self.last_move
            last_move = "Last move: black" if self.board_logic.get(self.last_move) == CellState.BLACK else "Last move: white"
            last_move = last_move + " (" + alphabetic_coordinate +", " + str(numeric_coordinate) + ")"

            font = pygame.font.Font(None, 28)
            text_surface = font.render(last_move, True, (0, 0, 0))
            screen.blit(text_surface, (700, 20))

    def draw_game_over(self, screen):
        if self.game_over:
            font = pygame.font.Font(None, 28)
            text_surface = font.render(f"Game over, winner is {self.winner}", True, (0, 0, 0))
            screen.blit(text_surface, (700, 600))

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
    def get_neighbors(self, coordinates, current_board_logic):
        L, N = coordinates
        char_code = ord(L)
        potential_neighbors = [
            (L,N-1), (L,N +1),
            (chr(char_code-1), N-1), (chr(char_code - 1), N),
            (chr(char_code+1), N), (chr(char_code+1), N+1)
        ]
        return[c for c in potential_neighbors if c in current_board_logic]        
#izmena ovde, dodato da koristi current_board_logic


#metoda koja proverava da li je kraj igre, za igraca koji je upravo odigrao potez
#dodat ptc kao player_to_check, za potrebu provere kada se potencijalno naislo na kraj igre u proveri u buducnost
    def is_game_over(self, current_board_logic, ptc):
        color = CellState.BLACK if ptc == Player.BLACK else CellState.WHITE
        islands = self.black_islands if ptc == Player.BLACK else self.white_islands

        for i in range(len(islands)):
            for j in range(i+1, len(islands)):
                if self._has_path(islands[i], islands[j], color, current_board_logic):
                    if (self.get_distances(islands[i], islands[j]) >= self.get_winning_treshold()):
                        return True

        if not any(v == CellState.EMPTY for v in current_board_logic.values()):
            for i in range(len(islands)):
                for j in range(i + 1, len(islands)):
                    if self._has_path(islands[i], islands[j], color, current_board_logic):
                        if self.get_distances(islands[i], islands[j]) >= 5:
                            return True
            return False

        return False
#izmena i ovde da koristi current_board_logic

#zapravo sam BFS koji za svaka 2 ostrva proverava da li su spojena na osnovu neighbor polja
    def _has_path(self, start_island, target_island, color, current_board_logic):
        queue = list(start_island)
        visited = set(start_island)
        while(queue):
            curr=queue.pop(0)
            if curr in target_island:
                return True
            for neighbor in self.get_neighbors(curr, current_board_logic):
                if neighbor not in visited and current_board_logic.get(neighbor) == color:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False
#dodato da koristi current_board_logic

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

    #metoda za nalazenje centralne koordinate u skladu sa velicinom cele table
    def center_coord(self):
        numeric_coordinate = self.board.size
        alphabetic_coordinate = chr(ord('A') + self.board.size - 1)
        return (alphabetic_coordinate, numeric_coordinate)

    #metoda za uparivanje dijagonalnih ostrva, u skladu sa winning thresholdom, da bi znali najbolji plan za povezivanje
    def pair_island(self, island):
        islands = self.white_islands if island in self.white_islands else self.black_islands
        for i in range(len(islands)):
            if (self.get_distances(islands[i], island) >= self.get_winning_treshold()):
                    return islands[i]
        return None
    
    #BFS algoritam za racunanje najmanjeg broja polja koji treba da se popuni da bi doslo do kraja igre, ima i setovanu pocetnu vrednost na 1000
    #u slucaju da drugi igrac prepreci put izmedju neka 2 dijagonalna ostrva
    def far_from_win(self, current_board_logic, islands, player):
        cell_color = CellState.WHITE if player == Player.WHITE else CellState.BLACK
        ret_value = 1000

        all_player_cells = set()
        for island in islands: 
            all_player_cells.update(island)
            pair_island = self.pair_island(island)
            pq = []
            visited = set()
            for coordinates in island:
                heapq.heappush(pq, (0, coordinates))
                visited.add(coordinates)

            while pq:
                value, coords = heapq.heappop(pq)
                if coords in pair_island:
                    ret_value = min(ret_value,value)
                    break
                        
                neighbors = self.get_neighbors(coords, current_board_logic)
                for neighbor in neighbors:
                    if neighbor in visited:
                        continue
                    if current_board_logic[neighbor] == CellState.EMPTY:
                        heapq.heappush(pq, (value+1, neighbor))
                    elif current_board_logic[neighbor] == cell_color or neighbor in all_player_cells:
                        heapq.heappush(pq, (value, neighbor))
                    visited.add(neighbor)
        return ret_value
    
#HEURISTICKA FUNKCIJA
#procenjuje stanje na tabli, tj ko trenutno ima prednost, predstavljeno kroz
#vrednost evaluation kao trenutno stanje, koje je - ili + u zavisnosti od igraca koji vodi
#uz edge kako bi se favorizovao ofanzivan pre nego defanzivan potez u situaciji da 
#su oba igraca jednako udaljena od pobede
    def evaluation(self, current_board_logic, player):
        #edge = 0.5 if player == Player.WHITE else -0.5
        white_value = self.far_from_win(current_board_logic, self.white_islands, Player.WHITE)
        black_value = self.far_from_win(current_board_logic, self.black_islands, Player.BLACK)
        
    #        white_value = (10 / (white_value + 0.1)) ** 2
    #        black_value = (10 / (black_value + 0.1)) ** 2

        evaluaton = black_value - white_value #+ edge
        #print (evaluaton)

        return evaluaton
    
#minimax (rekirzivni algoritam) zajedno sa alfa beta odsecanjem, i podesivom dubinom poteza unapred koji ce da se odigraju za proveru
    def minimax(self, current_board_logic, depth, alpha, beta, player):            
        
        if self.is_game_over(current_board_logic, Player.WHITE):
            return 1000 + depth
        if self.is_game_over(current_board_logic, Player.BLACK):
            return -1000 - depth

        if depth == 0:
            return self.evaluation(current_board_logic, player)
        
        moves = self.get_legal_moves(current_board_logic)
        if not moves:
            return self.evaluation(current_board_logic, player)

        if player == Player.WHITE:
            value = -math.inf
            for move in moves:
                new_board_logic = self.get_next_state(current_board_logic, move, player)
                value = max(
                    value,
                    self.minimax(new_board_logic, depth - 1, alpha, beta, Player.BLACK)
                )
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        else:
            value = math.inf
            for move in moves:
                new_board_logic = self.get_next_state(current_board_logic, move, player)
                value = min(
                    value,
                    self.minimax(new_board_logic, depth - 1, alpha, beta, Player.WHITE)
                )
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
        
#glavna funkcija koja poziva sve ostale metode. radi procenu svakog legalnog poteza da dobije najbolji u skladu sa trenutnom situacijom na tabli
#vraca listu najboljih poteza tako da moze da se odabere jedan od tih najboljih, da bi se napravila makar neka randomizacija, tj da se ne bi uvek igrao
#potpuno isti potez u istoj situaciji
    def best_move(self, current_board_logic, depth, player):  
        best_move = None
        best_moves = []
        if player == Player.WHITE:
            best_value = -math.inf
            alpha = -math.inf
            beta = math.inf

            moves = self.get_legal_moves(current_board_logic)
#            opponent = Player.BLACK
#            for move in moves:
#                test_state = self.get_next_state(current_board_logic, move, player)
#                if self.is_game_over(test_state, player):
#                    return move
                
#            for move in moves:
#                test_state = self.get_next_state(current_board_logic, move, opponent)
#                if self.is_game_over(test_state, opponent):
#                    return move
                
            for move in moves:
                new_board_logic = self.get_next_state(current_board_logic, move, player)
                value = self.minimax(new_board_logic, depth - 1, alpha, beta, Player.BLACK)
                if value == best_value:
                    best_moves.append(move)
                if value > best_value:
                    best_value = value
                    best_moves = []
                    best_moves.append(move)
                alpha = max(alpha, value)
        else:
            best_value = math.inf
            alpha = -math.inf
            beta = math.inf

            moves = self.get_legal_moves(current_board_logic)
#            opponent = Player.WHITE
#            for move in moves:
#                test_state = self.get_next_state(current_board_logic, move, player)
#                if self.is_game_over(test_state, player):
#                    return move
                
#            for move in moves:
#                test_state = self.get_next_state(current_board_logic, move, opponent)
#                if self.is_game_over(test_state, opponent):
#                    return move
                
            for move in moves:
                new_board_logic = self.get_next_state(current_board_logic, move, player)
                value = self.minimax(new_board_logic, depth - 1, alpha, beta, Player.WHITE)
                if value == best_value:
                    best_moves.append(move)
                if value < best_value:
                    best_value = value
                    best_moves = []
                    best_moves.append(move)
                beta = min(beta, value)
        
        # center_coord = self.center_coord()
        # min_dist = math.inf
        # for move in best_moves:
        #     if self.distance(move,center_coord)<min_dist:
        #         min_dist = self.distance(move,center_coord)
        #         best_move = move
        
        min_dist = math.inf
        
        for move in best_moves:
            d = self.distances_to_center.get(move, 999)
            if d < min_dist:
                min_dist = d
                best_move = move

        return best_move if best_move else random.choice(best_moves)
    
    def distance(self, start_coord, target_coord):
        if start_coord == target_coord:
            return 0
        
        queue = [(start_coord, 0)]
        visited = {start_coord}
        
        while queue:
            current, dist = queue.pop(0)
            
            if current == target_coord:
                return dist
            
            for neighbor in self.get_neighbors(current, self.board_logic):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return 999

    
#poziv metode best_move da dobijemo listu, pretvaranje u koordinate i odigravanje samog poteza
    def computer_move(self):
        if self.current_player == self.computer_color and not(self.game_over):
            best_move = self.best_move(self.board_logic, self.depth, self.computer_color)
            coordinates = self.inverse_convert_coordinates(best_move[0],best_move[1])
            return self.move(coordinates)
        return False