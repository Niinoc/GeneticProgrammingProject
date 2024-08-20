/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Project/Maven2/JavaApp/src/main/java/${packagePath}/${mainClassName}.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.FileNotFoundException;
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
            population.diverseIndividuals = nextPopulation.diverseIndividuals;
            population.diversity = nextPopulation.diversity;

            best = population.best();
            // --- Write log data after each generation ---
            Log.println("bestfitness", generation + ","
                                + best.getFitnessMSE()
        //                    + "," + best.getFitnessMAPE()
        //                    + "," + best.getFitnessR2()
        //                    + "," + best.getFitnessEVS()    //TODO entkommentieren für weitere Maße
                );

            //print progress in %
            int progress = (int) (100.0 * generation / numberOfGenerations);

                if (progress % 5 == 0 && progress != lastPrintedProgress) {
                    System.out.println(progress + "%");
                    lastPrintedProgress = progress;
                }

            if (best.getFitnessMSE() < 1e-11) {
                Global.numberOfGenerations = generation;   //setzt numOfGens auf Gen in der Funktion gefunden wurde
                break;    //früher Abbruch falls Funktion gefunden
            }
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
//        System.out.println("HashMap:");
//        for (Map.Entry<Individual, Integer> entry : population.diversIndividulas.entrySet()) {
//            if (entry.getValue() > 1) System.out.println(entry.getKey() + ": " + entry.getValue());
//        }

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
            population.add(new Individual(program,
                    fitnessFunction.evalMSE(program)
//                    ,fitnessFunction.evalMAPE(program)
//                    ,fitnessFunction.evalR2(program)
//                    ,fitnessFunction.evalEVS(program)     //TODO entkommentieren für weitere Maße
            ));
        }
        population.computeDiversityMap();
        population.computeDiversity();
        return population;
    }

    Population nextGenPopulation(Population oldPopulation) {
        Population nextPopulation = new Population(); // Create a new empty population
        for (int i = 0; i < populationSize; i++) { // and fill it with mutated offsprings.
            Program offspring = makeOffspring(oldPopulation);  //Create offprint program
            nextPopulation.add(new Individual(offspring,
                    fitnessFunction.evalMSE(offspring)
//                        ,fitnessFunction.evalMAPE(offspring)
//                        ,fitnessFunction.evalR2(offspring)
//                        ,fitnessFunction.evalEVS(offspring)   //TODO entkommentieren für weitere Maße
            )); // Compute fitness (takes a lot of time)
        }
        for (int i = 0; i < randomMigrantAmount; i++) {
            Program randomMigrant = Program.random(addedProgramLength);
            nextPopulation.add(new Individual(randomMigrant, fitnessFunction.evalMSE(randomMigrant)));
        }
        nextPopulation.computeDiversityMap();
        nextPopulation.computeDiversity();

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
        /*Individual parent3 = population.get(MyRandom.nextInt(population.size()));
        Individual parent4 = population.get(MyRandom.nextInt(population.size()));
        Individual parent5 = parent1.getFitnessMSE() < parent2.getFitnessMSE() ? parent1 : parent2;
        Individual parent6 =  parent3.getFitnessMSE() < parent4.getFitnessMSE() ? parent3 : parent4;
        return parent5.getFitnessMSE() < parent6.getFitnessMSE() ? parent5 : parent6;*/
        return parent1.getFitnessMSE() < parent2.getFitnessMSE() ? parent1 : parent2;
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

        if (parentProgram.instructions.size() < maxProgramLength && parentProgram.instructions.size() > 1) {
            // insert random instruction
            if ( MyRandom.nextDouble() < mutationProbabiltyInstructionInsertion) {
                offspring.instructions.add(Instruction.random());
            }
            // delete random instruction
            if (MyRandom.nextDouble() < mutationProbabiltyInstructionDeletion) {
                offspring.instructions.remove(MyRandom.nextInt(parentProgram.instructions.size()));
            }
        }

        //TODO: neue Mutationen hier

        return offspring;
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
        if (args.length >= 6 && Double.parseDouble(args[5]) >= 0 && Double.parseDouble(args[5]) <= 1) mutationProbabiltyInstructions = Double.parseDouble(args[5]);
        if (args.length >= 7 && Double.parseDouble(args[6]) >= 0 && Double.parseDouble(args[6]) <= 1) mutationProbabiltyInitialRegisterStates = Double.parseDouble(args[6]);
        if (args.length >= 8 && Double.parseDouble(args[7]) >= 0 && Double.parseDouble(args[7]) <= 1) mutationStrengthInitialRegisterStates = Double.parseDouble(args[7]);
        if (args.length >= 9) fitnessCasesFileName = args[8];
        if (args.length >= 10) logFolderPath = args[9];
    }
}
