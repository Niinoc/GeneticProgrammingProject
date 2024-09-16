/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Project/Maven2/JavaApp/src/main/java/${packagePath}/${mainClassName}.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 *
 * @author Peter
 */
public class GeneticProgramming extends Global {
    // Class Global holds all parameters.

    /**
     * *
     * Main method where execution starts.
     *
     * @param args Command line arguments (ignored here). (not anymore)
     */
    public static void main(String[] args) throws FileNotFoundException, UnsupportedEncodingException {
        parseAndSetArguments(args);

//        System.out.println("Seed: " + seed);

//        Log.fileNamePrefix = logFileNamePrefix; // You can change the log-output prefix in class Global

        fitnessFunction = new FitnessRegression(fitnessCasesFileName);  // Create a fitness function (objective function) from file

        GeneticProgramming gp = new GeneticProgramming(); // Create a gp instance (using the global fitnessFunction)

        gp.runOptimization();  // Run the optimization
    }

    /**
     * *
     * The main algorithm (genetic programming) runing the optimization.
     *
     */
    public void runOptimization() {

        Log.createLogFolder();

        Population population = newRandomPopulation();  // Create initial random population

        //check Diversity
        double startDiversity = population.diversity * 100;

        Individual best = population.best();
        Individual first = best;

        // System.out.println(population);

        // Logging ----
        Log.println("initialbehavior", fitnessFunction.evalInputOutputBehavior(first.getProgram()));
        Log.println("initialpopulation", "" + "startDiversity: " + startDiversity +"\n" + population);
        Log.println("fitnessFunction", "" + fitnessFunction);

        Log.println("bestfitness", "generation,FitnessMSE"); //bestfitness file header

        int lastPrintedProgress = -1; // for progess

        // Evolution loop
        for (int generation = 1; generation <= numberOfGenerations; generation++) {
            Population nextPopulation = nextGenPopulation(population);

            //TODO Note that the best individual can die. To avoid this you can uncomment the following line.
            nextPopulation.set(0, best); // Survival of the best ("elitist strategy")

            population = nextPopulation;

            best = population.best();
            // --- Write log data after each generation ---
            Log.println("bestfitness", generation + "," + best.getFitnessMSE());

            //print progress in %
                int progress = (int) (100.0 * generation / numberOfGenerations);

                if (progress % 5 == 0 && progress != lastPrintedProgress) {
                    System.out.println(progress + "%");
                    lastPrintedProgress = progress;
                }

            /*if (best.getFitnessMSE() < 1e-11) {
                Global.numberOfGenerations = generation;   //setzt numOfGens auf Gen in der Funktion gefunden wurde
                break;    //früher Abbruch falls Funktion gefunden
            }*/
        }

        Log.println("parameters", parametersToCSV());

        System.out.println("Best individual at generation " + numberOfGenerations);
        System.out.println(best);
        System.out.println(best.getProgram().toArithmetic());


        // --- Log final result ---
        // Store input-output behavior of final best program in a file
        Log.println("finalbehavior", "# final function: " +
                best.getProgram().toArithmetic() + "\n" +
                fitnessFunction.evalInputOutputBehavior(best.getProgram()));
        Log.println("finalprogram", "Best final individual: " + "\n" + best);

        double endDiversity = population.diversity * 100;

        Log.println("finalpopulation", "" + "endDiversity: " + endDiversity +"\n" + population);  // Store final population

        System.out.println("startDiversity: " + startDiversity +"\n"
                            +"endDiversity: " + endDiversity);

        validateFitnessConsistency(population);

//        System.out.println("HashMap:");
//        for (Map.Entry<Individual, Integer> entry : population.diversIndividulas.entrySet()) {
//            if (entry.getValue() > 1) System.out.println(entry.getKey() + ": " + entry.getValue());
//        }

    }

    private void validateFitnessConsistency(Population population) {
        Map<String, List<Individual>> individualsByArithmeticForm = new HashMap<>();
        double epsilon = 1e-30;  // Small tolerance for floating-point comparison

        for (Individual individual : population) {
            Program program = individual.getProgram();
            String arithmeticForm = program.getArithmeticForm();

            // Gruppiere Individuen nach ihrer arithmetischen Form
            individualsByArithmeticForm.computeIfAbsent(arithmeticForm, k -> new ArrayList<>()).add(individual);
        }

        int pairsFound = 0;

        for (Map.Entry<String, List<Individual>> entry : individualsByArithmeticForm.entrySet()) {
            List<Individual> individuals = entry.getValue();

            if (individuals.size() > 1) {
                for (int i = 0; i < individuals.size(); i++) {
                    for (int j = i + 1; j < individuals.size(); j++) {
                        Individual ind1 = individuals.get(i);
                        Individual ind2 = individuals.get(j);

                        // Überprüfe, ob die Instruktionen unterschiedlich sind
                        if (Math.abs(ind1.getFitnessMSE() - ind2.getFitnessMSE()) > epsilon) {
                            // Drucke die arithmetische Form und die Fitnesswerte der zwei Programme
                            System.out.println("Arithmetische Form: " + entry.getKey());
                            System.out.println("Individuum 1 Fitness: " + ind1.getFitnessMSE());
                            System.out.println("Individuum 2 Fitness: " + ind2.getFitnessMSE());
                            System.out.println("Individuum 1 Instruktionen: " + ind1.getProgram().instructions);
                            System.out.println("Individuum 2 Instruktionen: " + ind2.getProgram().instructions);
                            System.out.println("------------------------");

                            pairsFound++;
                            if (pairsFound >= 2) {
                                return;  // Stoppe nach 2 Paaren
                            }
                        }
                    }
                }
            }
        }
    }



    /**
     * *
     * Generates a new random population of individuals. An individual is a
     * program plus its fitness.
     *
     * @return the new population. Uses initialProgramLength and populationSize
     * as parameters.
     */
    Population newRandomPopulation() {
        Population population = new Population();
        for (int i = 0; i < populationSize; i++) {
            Program program = Program.random(addedProgramLength);
            population.add(new Individual(program));
        }
        population.computeFitnessAndDiversity(fitnessFunction);
        return population;
    }

    Population nextGenPopulation(Population oldPopulation) {
        Population nextPopulation = new Population(); // Create a new empty population

        for (int i = 0; i < populationSize/2; i++) { // and fill it with recombined and mutated offsprings.
            Program[] offsprings = makeOffsprings(oldPopulation);  //Create offprint program

            nextPopulation.add(new Individual(offsprings[0])); // Compute fitness (takes a lot of time)

            nextPopulation.add(new Individual(offsprings[1])); // Compute fitness (takes a lot of time)
        }

        // Check if the population size is less than the desired size due to rounding
        if (nextPopulation.size() < populationSize) {
            // Generate one more offspring
            Program extraOffspring = selectParent(oldPopulation).getProgram();
            extraOffspring = mutate(extraOffspring);
            nextPopulation.add(new Individual(extraOffspring));
        }

        nextPopulation.computeFitnessAndDiversity(fitnessFunction);
        return nextPopulation;
    }

    /**
     * *
     * Generates an offspring program for a given population. This includes
     * selecting a parent relative to its fitness. And creating mutated copy of
     * this parent.
     *
     * Here, RECOMBINATION could be added as another genetic operator.
     *
     * @param population
     * @return An offspring program.
     */
    public Program[] makeOffsprings(Population population) {
        Individual parent1 = selectParent(population); // select a parent based on fitness
        Individual parent2 = selectParent(population); // select a parent based on fitness
        // generate offsprings by copying and recombine the parents
        Program[] offspringPrograms = crossover(parent1.getProgram(), parent2.getProgram());
        // mutate offsprings
        offspringPrograms[0] = mutate(offspringPrograms[0]);
        offspringPrograms[1] = mutate(offspringPrograms[1]);
        return offspringPrograms;
    }

    /**
     * *
     * Select an individual from the population depending on its fitness. The
     * better the fitness, the more likely an individual is selected. This
     * generates a SELECTION PREASURE. Here, we just do a tournament of size
     * two, which generates a quite weak selection preasure.
     *
     * @param population
     * @return An individual selected.
     */
    public Individual selectParent(Population population) {
        return selectParentTournament(population);
    }

    /**
     * *
     * Method for tournament selection (tournament size 2).
     *
     * @param population The population selected from.
     * @return A selected individual.
     */
    public Individual selectParentTournament(Population population) {
        // we do a tournament selection, tournament size 2
        Individual parent1 = population.get(MyRandom.nextInt(population.size()));
        Individual parent2 = population.get(MyRandom.nextInt(population.size()));

        return parent1.getFitnessMSE() < parent2.getFitnessMSE() ? parent1 : parent2;
    }
    public Individual selectParentTournamentShared(Population population) {
        // we do a tournament selection, tournament size 2
        Individual parent1 = population.get(MyRandom.nextInt(population.size()));
        Individual parent2 = population.get(MyRandom.nextInt(population.size()));

        return parent1.getFitnessShared() < parent2.getFitnessShared() ? parent1 : parent2;
    }
    public Individual selectParentTournament3(Population population) {
        // we do a tournament selection, tournament size 3
        Individual parent1 = population.get(MyRandom.nextInt(population.size()));
        Individual parent2 = population.get(MyRandom.nextInt(population.size()));
        Individual parent3 = population.get(MyRandom.nextInt(population.size()));
        Individual parentTemp = parent1.getFitnessMSE() < parent2.getFitnessMSE() ? parent1 : parent2;
        return parent3.getFitnessShared() < parentTemp.getFitnessShared() ? parent3 : parentTemp;
    }

    /**
     * *
     * An alternative selection strategy chosing always the best individual.
     * Effectivle this leads to an (1,lambda)-strategy,here. That is,all
     * offsprings are generated only one parent.
     *
     * @param population
     * @return
     */
    public Individual selectParentBest(Population population) {
        return population.best();  // beware, this can take some time, since linear complexity
    }

    /**
     * *
     * Creates a mutated copy of the given (parent) program.
     * Note that the mutation operator is a critical element.
     * Here,you can play with its parametrization and its structure.
     * E.g., we might use changing mutation rates.
     * Or we can add a mutation that changes the length of a program.
     * 
     * @param parentProgram The parent.
     * @return A copy of the parent program with mutations.
     */
    public Program mutate(Program parentProgram) {
        Program offspring = new Program(parentProgram); // copy the parent

        // Mutate initial register states
        for (int i = 0; i < offspring.initialRegisterStates.length; i++) {
            if (MyRandom.nextDouble() < mutationProbabilityInitialRegisterStates) {  // mutation rate
                offspring.initialRegisterStates[i] = Program.randomRegisterValue();
            }
        }

        // Mutate instructions
        for (int i = 0; i < offspring.instructions.size(); i++) {
            if (MyRandom.nextDouble() < mutationProbabilityInstructions) {  // mutation rate
                // replace instruction by a random instruction
                offspring.instructions.set(i, Instruction.random());
            }
        }

        /*if (parentProgram.instructions.size() < maxProgramLength && parentProgram.instructions.size() > 1) {
            // insert random instruction
            if ( MyRandom.nextDouble() < mutationProbabiltyInstructionInsertion) {
                offspring.instructions.add(Instruction.random());
            }
            // delete random instruction
            if (MyRandom.nextDouble() < mutationProbabiltyInstructionDeletion) {
                offspring.instructions.remove(MyRandom.nextInt(parentProgram.instructions.size()));
            }
        }*/

        //TODO: neue Mutationen hier

        return offspring;
    }

    public Program[] crossover(Program parentProgram1, Program parentProgram2) {
        Program offspring1 = new Program(parentProgram1);
        Program offspring2 = new Program(parentProgram2);

        int size = offspring1.instructions.size();

        // Select two crossover points
        int crossoverPoint1 = MyRandom.nextInt(size);
        int crossoverPoint2 = MyRandom.nextInt(size - crossoverPoint1) + crossoverPoint1;

        // Perform crossover based on probability
        if (MyRandom.nextDouble() < crossoverProbability) {
            for (int i = crossoverPoint1; i <= crossoverPoint2; i++) {
                Instruction temp = offspring1.instructions.get(i);
                offspring1.instructions.set(i, parentProgram2.instructions.get(i));
                offspring2.instructions.set(i, temp);
            }
        }

        return new Program[]{offspring1, offspring2};  // Return both offspring
    }


    /**
     * *
     * setzt mitgegebene Parameter in Global und überprüft Richtigkeit
     * @param args
     * @author Nicholas
     */
    private static void parseAndSetArguments(String[] args) {
        if (args.length >= 1) seed = Long.parseLong(args[0]);
        if (args.length >= 2 && Integer.parseInt(args[1]) >= 1) numberOfFreeRegisters = Integer.parseInt(args[1]);
        if (args.length >= 3 && Integer.parseInt(args[2]) >= 1) addedProgramLength = Integer.parseInt(args[2]);
        if (args.length >= 4 && Integer.parseInt(args[3]) >= 1) populationSize = Integer.parseInt(args[3]);
        if (args.length >= 5) numberOfGenerations = Integer.parseInt(args[4]);
        if (args.length >= 6 && Double.parseDouble(args[5]) >= 0 && Double.parseDouble(args[5]) <= 1) mutationProbabilityInstructions = Double.parseDouble(args[5]);
        if (args.length >= 7 && Double.parseDouble(args[6]) >= 0 && Double.parseDouble(args[6]) <= 1) mutationProbabilityInitialRegisterStates = Double.parseDouble(args[6]);
        if (args.length >= 8 && Double.parseDouble(args[7]) >= 0 && Double.parseDouble(args[7]) <= 1) crossoverProbability = Double.parseDouble(args[7]);
        if (args.length >= 9) fitnessCasesFileName = args[8];
        if (args.length >= 10) logFolderPath = args[9];
    }
}
