/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Project/Maven2/JavaApp/src/main/java/${packagePath}/${mainClassName}.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

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

        System.out.println("Seed: " + seed);

        Log.fileNamePrefix = logFileNamePrefix; // You can change the log-output prefix in class Global

        fitnessFunction = new FitnessRegression();  // Create a fitness function (objective function)

        GeneticProgramming gp = new GeneticProgramming(); // Create a gp instance (using the global fitnessFunction)

        gp.runOptimization();  // Run the optimization
    }

    /**
     * *
     * The main algorithm (genetic programming) runing the optimization.
     *
     */
    public void runOptimization() {
        Log.println("parameters", toStringStatic());
        Population population = newRandomPopulation();  // Create initial random population

        // Logging ----
        System.out.println("\n--------------------------------");             //TODO printet Gen0 zweimal aus, aber einmal verändert
        // System.out.println(population);
        System.out.println("Best individual at generation " + 0);
        System.out.println(population.best());

        Log.println("initialbehavior",
                fitnessFunction.evalInputOutputBehavior(population.best().getProgram()) );
        Log.println("initialpopulation", "" + population);
        Log.println("fitnessFunction", "# The fitness function: " + fitnessFunction);

        // Evolution loop
        for (int generation = 1; generation <= numberOfGenerations; generation++) {
            Population nextPopulation = new Population(); // Create a new empty population
            for (int i = 0; i < populationSize; i++) { // and fill it with mutated offsprings.
                Program offspring = makeOffspring(population);  //Create offprint program
                nextPopulation.add(new Individual(offspring, fitnessFunction.eval(offspring))); // Compute fitness (takes a lot of time)
            }

            //TODO Note that the best individual can die. To avoid this you can uncomment the following line.

            // nextPopulation.set(0, population.best()); // Survival of the best ("elitist strategy")
            population = nextPopulation;

            // --- Write log data after each generation ---
            Log.println("bestfitness", generation + "\t" + population.best().getFitness());

        }

        System.out.println("Best individual at generation " + numberOfGenerations);
        System.out.println(population.best());
        System.out.println(fitnessFunction.toArithmetic(population.best().getProgram()));

        // --- Log final result --- 
        // Store input-output behavior of final best program in a file
        Log.println("finalbehavior",
                fitnessFunction.evalInputOutputBehavior(population.best().getProgram()));
        Log.println("finalprogram", "Best final individual: " + population.best());

        Log.println("finalpopulation", "" + population);  // Store final population

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
            Program program = Program.random(initialProgramLength);
            population.add(new Individual(program, fitnessFunction.eval(program)));
        }
        return population;
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
    public Program makeOffspring(Population population) {
        Individual parent = selectParent(population); // select a parent based on fitness
        Program offspringProgram = mutate(parent.getProgram()); // generate offspring by copying and mutating the parent
        return offspringProgram;
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
        // return selectParentTournament(population); 
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
        return parent1.getFitness() < parent2.getFitness() ? parent1 : parent2;
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
            if (MyRandom.nextDouble() < mutationProbabiltyInitialRegisterStates) {  // mutation rate
                offspring.initialRegisterStates[i]
                        += (MyRandom.nextDouble() - 0.5) * mutationStrengthInitialRegisterStates;
            }
        }

        // Mutate instructions
        for (int i = 0; i < offspring.instructions.size(); i++) {
            if (MyRandom.nextDouble() < mutationProbabiltyInstructions) {  // mutation rate
                // replace instruction by a random instruction
                offspring.instructions.set(i, Instruction.random());
            }
        }

        //TODO: neue Mutationen hier

        return offspring;
    }

    /**
     * *
     * setzt mitgegebene Parameter in Global und überprüft Richtigkeit
     *
     * @param args
     */
    private static void parseAndSetArguments(String[] args) {
        if (args.length >= 1) seed = Long.parseLong(args[0]);
        if (args.length >= 2 && Integer.parseInt(args[1]) >= 1) numberOfRegisters = Integer.parseInt(args[1]);
        if (args.length >= 3 && Integer.parseInt(args[2]) >= 1) initialProgramLength = Integer.parseInt(args[2]);
        if (args.length >= 4 && Integer.parseInt(args[3]) >= 1) populationSize = Integer.parseInt(args[3]);
        if (args.length >= 5) numberOfGenerations = Integer.parseInt(args[4]);
        if (args.length >= 6) numberOfFitnessCases = Integer.parseInt(args[5]);
        if (args.length >= 7 && Double.parseDouble(args[6]) >= 0 && Double.parseDouble(args[6]) <= 1) mutationProbabiltyInstructions = Double.parseDouble(args[6]);
        if (args.length >= 8 && Double.parseDouble(args[7]) >= 0 && Double.parseDouble(args[7]) <= 1) mutationProbabiltyInitialRegisterStates = Double.parseDouble(args[7]);
        if (args.length >= 9 && Double.parseDouble(args[8]) >= 0 && Double.parseDouble(args[8]) <= 1) mutationStrengthInitialRegisterStates = Double.parseDouble(args[8]);
        if (args.length >= 10) fitnessCasesFileName = args[9];
    }
}
