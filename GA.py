import numpy as np
import random
from tqdm.auto import tqdm
import subprocess
import PARCSsetup as parks
import concurrent.futures


class Population:

    def __init__(self, num_pop, n, chromosomes=[]):
        """
        :param: num_pop: number of population
                c: max value of one gene in chromosome
                n: size of square numpy nparray matrix
                chromosomes: list of chromosomes
        """
        self.chromosomes = chromosomes
        self.num_pop = num_pop
        self.n = n

    def count_adaptation(self, chromosome):
        """
        Count adaptation of each chromosome
        :param chromosome: numpay nxn array
        :return: float value of adaptation
        """
        parks.mod_file_path(chromosome.id)
        parks.write_array(chromosome.body)
        file_path = "res/Chromosome" + str(chromosome.id)
        subprocess.call(['p320mXX.exe', 'BEAVRS_20_HFP_MULTI_5_2018.INP'], shell=True, cwd=file_path,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        return parks.objective_function(parks.get_keff(chromosome.id))

    def create_population(self):
        """
        Create population of chromosomes and assign adaptation each of them
        """
        for i in range(self.num_pop):
            self.chromosomes.append(Chromosome(parks.create_array_v4(), i+1))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(self.count_adaptation, self.chromosomes)
        for result, chromosome in zip(results, self.chromosomes):
            chromosome.set_adaptation(result)
        self.write_best_chromosome(firstUse=True)

    def count_probabilities(self):
        """
        Count probability of choose each chromosome in crossing
        :return: list of probabilities in order of each chromosome
        """
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
        """
        :return: list of references to chromosomes that have been chosen to cross
        """
        choice = np.random.choice(self.chromosomes, self.num_pop, p=self.count_probabilities())
        return choice

    def crossing(self, parents):
        """
        Chromosomes corssover. Choose one random quarter and transplant it between two chromosomes
        :param parents: list of chromosomes, which were chose to cross before
        """
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
            self.chromosomes[i].set_body(parks.apply_mask(offspring[i].copy()))

    def mutation(self):
        """
        Mutation of each gene contained in chromosome with 2% chance
        """
        for chromosome in self.chromosomes:
            for i in range(self.n):
                for j in range(self.n):
                    if random.uniform(0, 100) < 0.2:
                        chromosome.body[i][j] = np.random.randint(1, 10)
            chromosome.set_body(parks.apply_mask(chromosome.body))
            # chromosome.set_adaptation(self.count_adaptation(chromosome))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(self.count_adaptation, self.chromosomes)
        for result, chromosome in zip(results, self.chromosomes):
            chromosome.set_adaptation(result)

    def best_chromosome(self):
        """
        Chose one of the best chromosome, based on adaptation
        :return: reference to the best chromosome
        """
        adaptations = []
        for chromosome in self.chromosomes:
            adaptations.append(chromosome.adaptation)
        best_adaptation = max(adaptations)
        for chromosome in self.chromosomes:
            if chromosome.adaptation == best_adaptation:
                return chromosome

    def write_best_chromosome(self,  firstUse):
        sum_adaptation = 0
        for chromosome in self.chromosomes:
            sum_adaptation += chromosome.adaptation
        average = sum_adaptation / self.num_pop
        best_chromosome = self.best_chromosome()
        var = self.count_variance()
        if firstUse:
            with open('res/data', 'w') as file:
                file.write("best\taverage\tvariance\n{}\t{}\t{}\n".format(
                            best_chromosome.adaptation, average, var))
        else:
            with open('res/data', 'a') as file:
                file.write("{}\t{}\t{}\n".format(best_chromosome.adaptation, average, var))

    def count_variance(self):
        numb_of_diff = 0
        for chromosome1 in self.chromosomes:
            for chromosome2 in self.chromosomes:
                for i in range(self.n):
                    for j in range(self.n):
                        if chromosome1.body[i][j] != chromosome2.body[i][j]:
                            numb_of_diff += 1
        return numb_of_diff/193

    def uranium_amount(self):
        enrichment = {
            1: 1.6, 2: 2.4, 3: 2.4, 4: 2.4, 5: 3.1, 6: 3.1, 7: 3.1, 8: 3.1, 9: 3.1
        }
        sum = 0
        for chromosome in self.chromosomes:
            for i in range(self.n):
                for j in range(self.n):
                    if chromosome.body[i][j] in enrichment:
                       sum += enrichment.get(chromosome.body[i][j])
        return sum


class Chromosome(Population):
    def __init__(self, body, id, adaptation=0):
        self.body = body
        self.id = id
        self.adaptation = adaptation

    def set_adaptation(self, adaptation):
        self.adaptation = adaptation

    def set_body(self, body):
        self.body = body

    def __str__(self):
        return str(self.body) + '\t' + str(self.adaptation) + "\n"


def main():
    n = 17  # only odd numbers
    num_pop = 2  # only even
    simulation = 1

    population = Population(num_pop, n)
    population.create_population()
    best_chromosome = population.best_chromosome()
    start_adaptation = best_chromosome.adaptation
    for _ in tqdm(range(simulation)):
        # print("", end='\r')
        parents = population.choose_parents()
        population.crossing(parents)
        population.mutation()
        population.write_best_chromosome(firstUse=False)
        if population.count_variance() < 0.5:
            break
    best_chromosome = population.best_chromosome()
    print(best_chromosome)
    final_adaptation = best_chromosome.adaptation
    print("increase of adaptation: {}%".format(int(((final_adaptation - start_adaptation)/start_adaptation) * 100)))


if __name__ == "__main__":
    main()
