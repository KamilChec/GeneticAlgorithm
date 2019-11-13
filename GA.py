import numpy as np
import random
from tqdm.auto import tqdm


class Population:
    def __init__(self, num_pop, c, n, chromosomes=[]):
        self.chromosomes = chromosomes
        self.num_pop = num_pop
        self.c = c
        self.n = n

    def count_adaptation(self, chromosome):
        counter = 0
        translation = int(chromosome.shape[0] / 2)
        for i in range(self.n):
            for j in range(self.n):
                z = self.c - (j - translation)**2 - (-i + translation)**2
                # counter += abs(z - chromosome[i][j])
                counter += (z - chromosome[i][j])**2
        return 1/counter

    def create_population(self):
        for i in range(self.num_pop):
            self.chromosomes.append(Chromosome(np.random.randint(1, self.c, size=(self.n, self.n))))
            self.chromosomes[i].set_adaptation(self.count_adaptation(self.chromosomes[i].body))

    def count_probabilities(self):
        sum_adp = 0
        for chromosome in self.chromosomes:
            sum_adp += chromosome.adaptation
        probabilities = []
        for chromosome in self.chromosomes:
            probabilities.append(chromosome.adaptation / sum_adp)
        norm_factor = 1 / sum(probabilities)
        normalised = []
        for probability in probabilities:
            normalised.append(norm_factor * probability)
        return normalised

    def choose_parents(self):
        choice = np.random.choice(self.chromosomes, self.num_pop, p=self.count_probabilities())
        return choice

    def crossing(self, parents):
        offspring = []
        available_parents = list(range(self.num_pop))
        for i in range(self.num_pop):
            if i % 2 == 0:
                x, y = np.random.randint(self.n, size=2)
                chosen_quarter = np.random.randint(1, 5)
            else:
                mother_idx = random.choice(available_parents)
                available_parents.remove(mother_idx)
                father_idx = random.choice(available_parents)
                available_parents.remove(father_idx)
                mother, father = parents[mother_idx].body.copy(), parents[father_idx].body.copy()
                if chosen_quarter == 1:
                    buff = father[:x, :y].copy()
                    father[:x, :y] = mother[:x, :y].copy()
                    mother[:x, :y] = buff.copy()
                elif chosen_quarter == 2:
                    buff = father[:x, y:].copy()
                    father[:x, y:] = mother[:x, y:].copy()
                    mother[:x, y:] = buff.copy()
                elif chosen_quarter == 3:
                    buff = father[x:, :y].copy()
                    father[x:, :y] = mother[x:, :y].copy()
                    mother[x:, :y] = buff.copy()
                elif chosen_quarter == 4:
                    buff = father[x:, y:].copy()
                    father[x:, y:] = mother[x:, y:].copy()
                    mother[x:, y:] = buff.copy()
                offspring.append(father.copy())
                offspring.append(mother.copy())
        for i in range(self.num_pop):
            self.chromosomes[i].set_body(offspring[i].copy())

    def mutation(self):
        for chromosome in self.chromosomes:
            for i in range(self.n):
                for j in range(self.n):
                    if random.uniform(0, 100) < 0.01:
                        chromosome.body[i][j] = np.random.randint(1, self.c)
            chromosome.set_adaptation(self.count_adaptation(chromosome.body))

    def best_chromosome(self):
        adaptations = []
        for chromosome in self.chromosomes:
            adaptations.append(chromosome.adaptation)
        best_adaptation = max(adaptations)
        for chromosome in self.chromosomes:
            if chromosome.adaptation == best_adaptation:
                return chromosome


class Chromosome(Population):
    def __init__(self, body, adaptation=0):
        self.body = body
        self.adaptation = adaptation

    def set_adaptation(self, adaptation):
        self.adaptation = adaptation

    def set_body(self, body):
        self.body = body

    def __str__(self):
        return str(self.body) + '\t' + str(self.adaptation)


def main():
    n = 11  # only odd numbers
    c = 50
    num_pop = 50  # only even
    simulation = 10000
    population = Population(num_pop, c, n)
    population.create_population()
    best_chromosome = population.best_chromosome()
    print(best_chromosome)
    start_adaptation = best_chromosome.adaptation
    parents = population.choose_parents()
    population.crossing(parents)
    population.mutation()
    print(1 / population.count_adaptation(best_chromosome.body))
    for i in tqdm(range(simulation)):
        # print("", end='\r')
        parents = population.choose_parents()
        population.crossing(parents)
        population.mutation()
    best_chromosome = population.best_chromosome()
    print(best_chromosome)
    final_adaptation = best_chromosome.adaptation
    print(int(((final_adaptation - start_adaptation)/start_adaptation) * 100))
    print(1/population.count_adaptation(best_chromosome.body))


if __name__ == "__main__":
    main()
