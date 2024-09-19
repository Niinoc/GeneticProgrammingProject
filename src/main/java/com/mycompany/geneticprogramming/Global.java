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

    static int numberOfRegisters = 10;           // Must be greater equal to the number of inputs, so this will now be added to numberOfInputs
    static int ProgramLength = 10;        // Length is fixed, this will also be added to numberOfInputs (new Mutation already implemented)


    static int populationSize = 200;

    static int numberOfGenerations = 10000;

    static int numberOfFitnessCases = 100;   //wird als Variable nur für alternativen Konstruktor verwendet
    static double stepSize = 1;             //wird nur für alternativen Konstruktor verwendet

    static int numberOfInputs = 1;          //wird als Variable nur für alternativen Konstruktor verwendet


    static double mutationProbabilityInstructions = 0.1;
    static double mutationProbabilityInitialRegisterStates = 0.3;
    static double crossoverProbability = 0.2;


    //Mutationen werden nicht verwendet
    static double mutationProbabilityInstructionInsertion = 0.0;
    static double mutationProbabilityInstructionDeletion = 0.0;
    static int maxProgramLength = 100;

    static FitnessFunction fitnessFunction;

    static String parametersToCSV() {
        return "seed," + seed + "\n" +
                "numberOfInputs," + numberOfInputs + "\n" +
                "numberOfRegisters," + numberOfRegisters + "\n" +
                "initialProgramLength," + ProgramLength + "\n" +
                "populationSize," + populationSize + "\n" +
                "numberOfGenerations," + numberOfGenerations + "\n" +
                "numberOfFitnessCases," + numberOfFitnessCases + "\n" +
                "mutationProbabilityInstructions," + mutationProbabilityInstructions + "\n" +
                "mutationProbabilityInitialRegisterStates," + mutationProbabilityInitialRegisterStates + "\n" +
                "mutationStrengthInitialRegisterStates," + crossoverProbability + "\n" +
                "FitnessCasesFileName," + fitnessCasesFileName + "\n" +
                "logFileNamePrefix," + logFileNamePrefix + "\n" +
                "logFileNamePostfix," + logFileNamePostfix;
    }

    static String parametersToString() {
        return "Parameters:\n" +
                "seed: " + seed + "\n" +
                "numberOfInputs: " + numberOfInputs + "\n" +
                "numberOfRegisters: " + numberOfRegisters + "\n" +
                "initialProgramLength: " + ProgramLength + "\n" +
                "populationSize: " + populationSize + "\n" +
                "numberOfGenerations: " + numberOfGenerations + "\n" +
                "numberOfFitnessCases: " + numberOfFitnessCases + "\n" +
                "mutationProbabilityInstructions: " + mutationProbabilityInstructions + "\n" +
                "mutationProbabilityInitialRegisterStates: " + mutationProbabilityInitialRegisterStates + "\n" +
                "mutationStrengthInitialRegisterStates: " + crossoverProbability + "\n" +
                "FitnessCasesFileName: " + fitnessCasesFileName + "\n" +
                "logFileNamePrefix: " + logFileNamePrefix + "\n" +
                "logFileNamePostfix: " + logFileNamePostfix;
    }

    static String parametersToStringShort(){
        return "["
                + seed +"|"
                + numberOfInputs +"|"
                + numberOfRegisters +"|"
                + ProgramLength +"|"
                + populationSize +"|"
                + numberOfGenerations +"|"
                + numberOfFitnessCases +"|"
                + mutationProbabilityInstructions +"|"
                + mutationProbabilityInitialRegisterStates +"|"
                + crossoverProbability +"|"
                + fitnessCasesFileName
                +"]";
    }


}
