/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

/**
 * Global parameter of the genetic programing system.
 * To keep things simple, parameters are global and defined here as static class variables.
 * All classes (that need these parameters) are derived from Global.
 * 
 * @author Peter & Nicholas
 */
public class Global {
    // Do NOT add non-static variables here!

    static String logFileNamePrefix = "out.";   // Here you can change the prefix of the log-files

    static String inputFileNamePrefix = "in.";
    
    static String logFileNamePostfix = ".txt";

    static String logFolderPath = "log/";
    static String inputFolderPath = "in/";

    static String fitnessCasesFileName = "I.11.19";

    static long seed = System.currentTimeMillis() + (Runtime.getRuntime().freeMemory() % 100000) + getProcessId();  // Seed for MyRandom
    private static long getProcessId() {
        String processName =
                java.lang.management.ManagementFactory.getRuntimeMXBean().getName();
        return Long.parseLong(processName.split("@")[0]);
    }

    static int numberOfFreeRegisters = 5;           // Must be greater equal to the number of inputs, so this will now be added to numberOfInputs
    static int addedProgramLength = 15;        // Length is fixed, this will also be added to numberOfInputs (new Mutation already implemented)

    static int maxProgramLength = 100;

    static int populationSize = 120;

    static int numberOfGenerations = 1000;

    static int numberOfFitnessCases = 50;
    static double stepSize = 1;

    static int numberOfInputs = 1;


    static double mutationProbabiltyInstructions = 0.1;
    static double mutationProbabiltyInitialRegisterStates = 0.3;
    static double mutationStrengthInitialRegisterStates = 0.2;
    static double mutationProbabiltyInstructionInsertion = 0.0;
    static double mutationProbabiltyInstructionDeletion = 0.0;

    static FitnessFunction fitnessFunction;

    static String parametersToString() {
        return "Parameters:\n" +
                "seed: " + seed + "\n" +
                "numberOfRegisters: " + numberOfFreeRegisters + "\n" +
                "initialProgramLength: " + addedProgramLength + "\n" +
                "populationSize: " + populationSize + "\n" +
                "numberOfGenerations: " + numberOfGenerations + "\n" +
                "numberOfFitnessCases: " + numberOfFitnessCases + "\n" +
                "mutationProbabilityInstructions: " + mutationProbabiltyInstructions + "\n" +
                "mutationProbabilityInitialRegisterStates: " + mutationProbabiltyInitialRegisterStates + "\n" +
                "mutationStrengthInitialRegisterStates: " + mutationStrengthInitialRegisterStates + "\n" +
                "FitnessCasesFileName: " + fitnessCasesFileName + "\n" +
                "logFileNamePrefix: " + logFileNamePrefix + "\n" +
                "logFileNamePostfix: " + logFileNamePostfix;
    }

    static String parametersToCSV() {
        return "seed," + seed + "\n" +
                "numberOfRegisters," + numberOfFreeRegisters + "\n" +
                "initialProgramLength," + addedProgramLength + "\n" +
                "populationSize," + populationSize + "\n" +
                "numberOfGenerations," + numberOfGenerations + "\n" +
                "numberOfFitnessCases," + numberOfFitnessCases + "\n" +
                "mutationProbabilityInstructions," + mutationProbabiltyInstructions + "\n" +
                "mutationProbabilityInitialRegisterStates," + mutationProbabiltyInitialRegisterStates + "\n" +
                "mutationStrengthInitialRegisterStates," + mutationStrengthInitialRegisterStates + "\n" +
                "FitnessCasesFileName," + fitnessCasesFileName + "\n" +
                "logFileNamePrefix," + logFileNamePrefix + "\n" +
                "logFileNamePostfix," + logFileNamePostfix;
    }

    static String parametersToStringShort(){
        return "["
                +seed +"|"
                + numberOfFreeRegisters +"|"
                + addedProgramLength +"|"
                +populationSize +"|"
                +numberOfGenerations +"|"
                +numberOfFitnessCases +"|"
                +mutationProbabiltyInstructions +"|"
                +mutationProbabiltyInitialRegisterStates +"|"
                +mutationStrengthInitialRegisterStates +"|"
                +fitnessCasesFileName
                +"]";
    }


}
