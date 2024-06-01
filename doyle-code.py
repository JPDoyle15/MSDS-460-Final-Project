import simpy
import random

class Player:
    def __init__(self, name, batting_average, on_base_percentage, slugging_percentage):
        self.name = name
        self.batting_average = batting_average
        self.on_base_percentage = on_base_percentage
        self.slugging_percentage = slugging_percentage

class Team:
    def __init__(self, name, lineup):
        self.name = name
        self.lineup = lineup
        self.current_batter_index = 0
        self.score = 0

    def get_next_batter(self):
        batter = self.lineup[self.current_batter_index]
        self.current_batter_index = (self.current_batter_index + 1) % len(self.lineup)
        return batter

class BaseballGame:
    def __init__(self, env, team1, team2, log_file):
        self.env = env
        self.team1 = team1
        self.team2 = team2
        self.current_inning = 1
        self.half_inning = 'top'  
        self.outs = 0
        self.bases = [None, None, None]  
        self.log_file = log_file

    def play_game(self):
        while self.current_inning <= 9:
            yield self.env.process(self.play_half_inning(self.team1 if self.half_inning == 'top' else self.team2))
            self.half_inning = 'bottom' if self.half_inning == 'top' else 'top'
            if self.half_inning == 'top':
                self.current_inning += 1

    def play_half_inning(self, team):
        self.outs = 0
        self.bases = [None, None, None]
        while self.outs < 3:
            batter = team.get_next_batter()
            yield self.env.process(self.at_bat(batter, team))

    def at_bat(self, batter, team):
        result = self.simulate_at_bat(batter)
        self.log_at_bat(batter, team, result)
        if result == 'single':
            self.advance_runners_single(batter, team)
        elif result == 'double':
            self.advance_runners_double(batter, team)
        elif result == 'triple':
            self.advance_runners_triple(batter, team)
        elif result == 'home_run':
            self.advance_runners_home_run(batter, team)
        elif result == 'walk':
            self.advance_runners_walk(batter, team)
        else:  # 'out'
            self.outs += 1
        yield self.env.timeout(1) 

    def simulate_at_bat(self, batter):
        outcomes = ['single', 'double', 'triple', 'home_run', 'walk', 'out']

        ba = batter.batting_average
        obp = batter.on_base_percentage
        slg = batter.slugging_percentage
        hit_prob = ba
        walk_prob = obp - ba
        single_prob = hit_prob * 0.6 
        double_prob = hit_prob * 0.2 
        triple_prob = hit_prob * 0.05  
        home_run_prob = hit_prob * 0.15 
        out_prob = 1 - obp
        probabilities = [single_prob, double_prob, triple_prob, home_run_prob, walk_prob, out_prob]
        return random.choices(outcomes, probabilities)[0]

    def advance_runners_single(self, batter, team):
        if self.bases[2] is not None:
            team.score += 1
        if self.bases[1] is not None:
            self.bases[2] = self.bases[1]
        if self.bases[0] is not None:
            self.bases[1] = self.bases[0]
        self.bases[0] = batter

    def advance_runners_double(self, batter, team):
        if self.bases[2] is not None:
            team.score += 1
        if self.bases[1] is not None:
            team.score += 1
        if self.bases[0] is not None:
            self.bases[2] = self.bases[0]
        self.bases[1] = batter
        self.bases[0] = None

    def advance_runners_triple(self, batter, team):
        if self.bases[2] is not None:
            team.score += 1
        if self.bases[1] is not None:
            team.score += 1
        if self.bases[0] is not None:
            team.score += 1
        self.bases[2] = batter
        self.bases[1] = None
        self.bases[0] = None

    def advance_runners_home_run(self, batter, team):
        if self.bases[2] is not None:
            team.score += 1
        if self.bases[1] is not None:
            team.score += 1
        if self.bases[0] is not None:
            team.score += 1
        team.score += 1 
        self.bases = [None, None, None]

    def advance_runners_walk(self, batter, team):
        if self.bases[2] is not None and self.bases[1] is not None and self.bases[0] is not None:
            team.score += 1
        if self.bases[1] is not None and self.bases[0] is not None:
            self.bases[2] = self.bases[1]
        if self.bases[0] is not None:
            self.bases[1] = self.bases[0]
        self.bases[0] = batter

    def log_at_bat(self, batter, team, result):
        bases_status = ''.join(['X' if player else 'O' for player in self.bases])
        with open(self.log_file, 'a') as f:
            f.write(f"Inning {self.current_inning} ({self.half_inning}): {batter.name} - {result}\n")
            f.write(f"Score: {self.team1.name} {self.team1.score}, {self.team2.name} {self.team2.score}\n")
            f.write(f"Outs: {self.outs}, Bases: {bases_status}\n\n")

team1_lineup = [
    Player("Volpe", 0.282, 0.355, 0.435),
    Player("Soto", 0.310, 0.408, 0.571),
    Player("Rizzo", 0.250, 0.316, 0.377),
    Player("Judge", 0.279, 0.410, 0.629),
    Player("Torres", 0.228, 0.301, 0.327),
    Player("Verdugo", 0.261, 0.324, 0.431),
    Player("Stanton", 0.235, 0.283, 0.497),
    Player("Cabrera", 0.247, 0.286, 0.360),
    Player("Trevino", 0.283, 0.327, 0.434)
]
team2_lineup = [
    Player("Duran", 0.266, 0.331, 0.446),
    Player("Rafaela", 0.209, 0.234, 0.363),
    Player("Devers", 0.273, 0.369, 0.528),
    Player("Abreu", 0.284, 0.359, 0.500),
    Player("O'Neill", 0.236, 0.343, 0.500),
    Player("Wong", 0.326, 0.368, 0.477),
    Player("Valdez", 0.156, 0.186, 0.267),
    Player("McGuire", 0.241, 0.323, 0.361),
    Player("Yoshida", 0.275, 0.348, 0.388)
]

team1 = Team("Team1", team1_lineup)
team2 = Team("Team2", team2_lineup)

env = simpy.Environment()

log_file = 'game_log.txt'
with open(log_file, 'w') as f:
    f.write("Baseball Game Log\n\n")

game = BaseballGame(env, team1, team2, log_file)

env.process(game.play_game())
env.run()

print(f"Final Score: {team1.name} {team1.score} - {team2.name} {team2.score}")
