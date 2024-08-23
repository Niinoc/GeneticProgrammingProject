/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.IOException;
import java.util.ArrayList;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.stream.Stream;


/**
 * Just a one dimensional regression problem.
 * Given a target function, a number of fitness cases are generated.
 * The fitness of a program is the average squared error on the fitness cases.
 * The target function can be changed below.
 * 
 * @author Peter & Nicholas
 */
public class FitnessRegression extends FitnessFunction {
    Interpreter interpreter;
    ArrayList<ArrayList<Double>> fitnessCasesInput = new ArrayList<>();
    ArrayList<Double> fitnessCasesOutput = new ArrayList<>();

    /**
     * *
     * The target function of the one-dimensional regression problem.
     * This is what we try to find. 
     * @param x Input value
     * @return Output value
     */
    double targetFunction(double x) {
        return x;
    }

    /***
     * Instantiate a fitness function by generating a number of fitness cases.
     * A fitness case is one desired input-output pair.
     */
    public FitnessRegression() {
        for (int i = 0; i < numberOfFitnessCases; i++) {
            double input = (double) (i - numberOfFitnessCases / 2) * stepSize;
            double output = targetFunction(input);
            ArrayList<Double> inputList = new ArrayList<>();
            inputList.add(input);
            fitnessCasesInput.add(inputList);
            fitnessCasesOutput.add(output);
        }
    }
    public FitnessRegression(String fileName) {
        String filePath = inputFolderPath + inputFileNamePrefix + fileName + logFileNamePostfix;

        try (Stream<String> lines = Files.lines(Paths.get(filePath))) {
            lines.forEach(line -> {
                String[] parts = line.split("\\s+"); //split in and output by "  "
                ArrayList<Double> inputList = new ArrayList<>();
                for (int i = 0; i < parts.length-1; i++) {
                    inputList.add(Double.parseDouble(parts[i]));
                }
                fitnessCasesInput.add(inputList);
                double outputValue = Double.parseDouble(parts[parts.length-1].trim());
                fitnessCasesOutput.add(outputValue);
            });
            //overrides important static variables in Global after Input Read-out
            Global.numberOfFitnessCases = fitnessCasesInput.size();
            Global.numberOfInputs = fitnessCasesInput.get(0).size();
            Global.numberOfFreeRegisters += numberOfInputs;
            Global.addedProgramLength += numberOfInputs;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /*** 
     * Computes the fitness of a given program.
     * @param program
     * @return The fitness of the program.
     */
    @Override
    public Double evalMSE(Program program) {
        if (interpreter == null || !interpreter.getProgram().equals(program)) {
            interpreter = new Interpreter(program);
        } // instantiate an interpreter that runs the program, if necessary

        double errorSum = 0.0;    // here we collect the error the program makes on the fitness cases

        for (int i = 0; i < numberOfFitnessCases; i++) {                // For each fitness case
            double result = interpreter.run(fitnessCasesInput.get(i));  // Run the program
            if (Double.isFinite(result)) {
                // Normal fitness calculation
                result -= fitnessCasesOutput.get(i);    // And compare the output of the program with the desired output.
                errorSum += result * result;
            } else {
                // Penalize heavily for invalid results
                return Double.POSITIVE_INFINITY;
            }
        }

        return errorSum / numberOfFitnessCases;     //return the average error as the fitness
    }

    //region R2 Score, Explained Varianz Score, MAPE
    @Override
    public Double evalMAPE(Program program) {
        interpreter = new Interpreter(program); // instantiate an interpreter that runs the program

        double totalAbsolutePercentageError = 0;

        for (int i = 0; i < numberOfFitnessCases; i++) {
            double actual = fitnessCasesOutput.get(i);
            double predicted = interpreter.run(fitnessCasesInput.get(i));
            double absolutePercentageError = Math.abs((actual - predicted) / actual);

            totalAbsolutePercentageError += absolutePercentageError;
        }

        return (totalAbsolutePercentageError / numberOfFitnessCases) * 100;
    }

    // Helper method to calculate the mean of the actual outputs
    private double calculateMeanOutput() {
        double meanOutput = 0;
        for (int i = 0; i < numberOfFitnessCases; i++) {
            meanOutput += fitnessCasesOutput.get(i);
        }
        return meanOutput / numberOfFitnessCases;
    }

    // Helper method to calculate the sum of squared residuals (ssRes) and total sum of squares (ssTot)
    private double[] calculateSums(Program program, double meanOutput) {
        interpreter = new Interpreter(program);

        double ssRes = 0;
        double ssTot = 0;

        for (int i = 0; i < numberOfFitnessCases; i++) {
            double actual = fitnessCasesOutput.get(i);
            double predicted = interpreter.run(fitnessCasesInput.get(i));
            double residual = actual - predicted;

            ssRes += residual * residual;
            ssTot += (actual - meanOutput) * (actual - meanOutput);
        }

        return new double[] {ssRes, ssTot};
    }

    @Override
    public Double evalR2(Program program) {
        double meanOutput = calculateMeanOutput();
        double[] sums = calculateSums(program, meanOutput);

        double ssRes = sums[0];
        double ssTot = sums[1];

        // Calculate R² score
        return 1 - (ssRes / ssTot);
    }

    @Override
    public Double evalEVS(Program program) {
        double meanOutput = calculateMeanOutput();
        double[] sums = calculateSums(program, meanOutput);

        double ssRes = sums[0];
        double ssTot = sums[1];

        // Calculate explained variance
        return (ssTot - ssRes) / ssTot;
    }
    //endregion

    /***
     * Computes the input output behavior of the program in the same way as the fitness is evaluated.
     * Can be used to make a plot what we have learned.
     * format: CSV
     * @param program
     * @return All input output pairs used for fitness calculation. The last column is the target value.
     */

    @Override
    public String evalInputOutputBehavior(Program program) {
        StringBuilder result = new StringBuilder();
        interpreter = new Interpreter(program);     // instantiate an interpreter that runs the program

        // Header für CSV-Datei
        for (int i = 0; i<numberOfInputs; i++) {
            result.append("Input").append(i).append(",");
        }
        result.append("Output").append("Expected Output").append("\n");

        for (int i = 0; i < numberOfFitnessCases; i++) {    // For each fitness case
            ArrayList<Double> inputList = fitnessCasesInput.get(i);
            for (double input : inputList) {
                result.append(input).append(",");
            }
            double output = interpreter.run(inputList);
            result.append(output).append(",").append(fitnessCasesOutput.get(i)).append("\n");
        }

        return result.toString();  //return the average error as the fitness
    }


    /***
     * For printing the fitness cases in CSV format.
     * @return A string describing the fitness function including the fitness cases.
     */

    @Override
    public String toString() {
        StringBuilder result = new StringBuilder();

        // Header für CSV-Datei
        result.append("# FitnessFunction: FitnessRegression\n");
        result.append("# numberOfFitnessCases:,").append(numberOfFitnessCases).append("\n");
        for (int i = 0; i<numberOfInputs; i++) {
            result.append("Input").append(i).append(",");
        }
        result.append("Expected Output\n");

        for (int i = 0; i < numberOfFitnessCases; i++) {
            for (double x : fitnessCasesInput.get(i)) {
                result.append(x).append(",");
            }
            result.append(fitnessCasesOutput.get(i)).append("\n");
        }

        return result.toString();
    }


}
