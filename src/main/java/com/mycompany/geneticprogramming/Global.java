/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Global parameter of the genetic programing system.
 * To keep things simple, parameters are global and defined here as static class variables.
 * All classes (that need these parameters) are derived from Global.
 * 
 * @author Peter
 */
public class Global {
    // Do NOT add non-static variables here!

    static String logFileNamePrefix = "out.";   // Here you can change the prefix of the log-files

    static String inputFileNamePrefix = "in.";
    
    static String logFileNamePostfix = ".txt";

    static String fitnessCasesFileName = "fitnessCases";

    static long seed = System.currentTimeMillis() + (Runtime.getRuntime().freeMemory() % 100000) + getProcessId();  // Seed for MyRandom
    private static long getProcessId() {
        String processName =
                java.lang.management.ManagementFactory.getRuntimeMXBean().getName();
        return Long.parseLong(processName.split("@")[0]);
    }

    static int numberOfRegisters = 5;           // Must be greater equal to the number of inputs, here the number of inputs is 1.
    static int initialProgramLength = 5;        // In the current version, the length of a program is fixed.

    static int maxProgramLength = 100;

    static int numberOfGenerations = 1000;

    static int numberOfFitnessCases = 1;    //damit er keinen mist macht, passt nicht, komisch what ever

    static int numberOfFitnessCases = 50;
    static double stepSize = 1;

    static int numberOfInputs = 1;


    static double mutationProbabiltyInstructions = 0.1;
    static double mutationProbabiltyInitialRegisterStates = 0.3;
    static double mutationStrengthInitialRegisterStates = 0.2;
    static double mutationProbabiltyInstructionInsertion = 0.01;
    static double mutationProbabiltyInstructionDeletion = 0.01;

    static FitnessFunction fitnessFunction;

    static String toStringStatic() {
        return "Parameters:\n" +
                "seed: " + seed + "\n" +
                "numberOfRegisters: " + numberOfRegisters + "\n" +
                "initialProgramLength: " + initialProgramLength + "\n" +
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

    static String toStringShort(){
        return "["
                +seed +"|"
                +numberOfRegisters +"|"
                +initialProgramLength +"|"
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
