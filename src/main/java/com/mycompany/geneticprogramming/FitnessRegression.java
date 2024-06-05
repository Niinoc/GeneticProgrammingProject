/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
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
 * @author Peter
 */
public class FitnessRegression extends FitnessFunction {
    Interpreter interpreter;
    
    int numberOfInputs = 1;

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
        String filePath = inputFileNamePrefix + fileName + logFileNamePostfix;

        try (Stream<String> lines = Files.lines(Paths.get(filePath))) {
            lines.forEach(line -> {
                String[] parts = line.split("--> ");
                if (parts.length == 2) {
                    double inputValue = Double.parseDouble(parts[0].trim());
                    double outputValue = Double.parseDouble(parts[1].trim());
                    ArrayList<Double> inputList = new ArrayList<>();
                    inputList.add(inputValue);
                    fitnessCasesInput.add(inputList);
                    fitnessCasesOutput.add(outputValue);
                }
            });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //TODO in abhängigkeit der parts.length ne schleife für alle inputs

    /***
     * This function returns the number of inputs of a fitness case
     * and thus the number of inputs a learned program should have.
     * Here, it is simply 1.
     * @return
     */
    @Override
    public int getNumberOfInputs() {
        return numberOfInputs;
    }

    /*** 
     * Computes the fitness of a given program.
     * @param program
     * @return The fitness of the program.
     */
    @Override
    public Double evalMSE(Program program) {
        interpreter = new Interpreter(program); // instantiate an interpreter that runs the program

        double errorSum = 0;    // here we collect the error the program makes on the fitness cases
        for (int i = 0; i < numberOfFitnessCases; i++) {    // For each fitness case
            double error = interpreter.run(fitnessCasesInput.get(i)) - fitnessCasesOutput.get(i);   // Run the program
            errorSum += error * error;  // And compare the output of the program with the desired output.
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
     * @param program
     * @return All input output pairs used for fitness calculation. The last column is the target value.
     */
 
    @Override
    public String evalInputOutputBehavior(Program program) {
        StringBuilder result = new StringBuilder();
        interpreter = new Interpreter(program);     // instantiate an interpreter that runs the program

        double[] inputs = new double[numberOfFitnessCases];     //für plotter
        double[] outputs = new double[numberOfFitnessCases];    //für plotter

        for (int i = 0; i < numberOfFitnessCases; i++) {    // For each fitness case
            ArrayList<Double> inputList = fitnessCasesInput.get(i);
            for (double input : inputList) {
                result.append(input).append("\t");      //für plotter
            }
            double output = interpreter.run(inputList);
            result.append(output).append("\t").append(fitnessCasesOutput.get(i)).append("\n");
            inputs[i] = inputList.get(0);
            outputs[i] = output;
        }

//        new GraphPlotter(inputs, outputs, fitnessCasesOutput);  //TODO für java plot entkommentieren

        return result.toString();  //return the average error as the fitness
    }

    /**
     * Converts the program to an arithmetic function as a string.
     * @return A string representing the arithmetic function.
     * @author Nicholas
     */
    public String toArithmetic(Program program) {
        StringBuilder function = new StringBuilder();
//        function.append("f(x) = ");

        // Mapping für die Registerausdrücke
        Map<Integer, String> registerExpressions = new HashMap<>();

        // Initialisierung der Ausdrücke für die Eingaberegister
        registerExpressions.put(0, "x");
        for (int i = 1; i < program.getNumberOfRegisters(); i++) {
            registerExpressions.put(i, String.valueOf((program.initialRegisterStates[i])));
        }

        int lastWrittenRegister = 0;

        // Auswertung der Anweisungen
        for (Instruction instruction : program.instructions) {

            int targetRegister = instruction.operands[0];
            lastWrittenRegister = targetRegister;
            //region baut Ausdruck
                Operator operator = instruction.operator;
                String operation = operator.toString();

            // Ausdrücke für Operanden
                String operand1Expression = "";
                String operand2Expression = "";
                String expression = "";
            if (operator.numberOfOperands == 2) {
                    operand1Expression = registerExpressions.get(instruction.operands[1]);
                expression = String.format("%s(%s)", operation, operand1Expression);

            } else {
                    operand1Expression = registerExpressions.get(instruction.operands[1]);
                    operand2Expression = registerExpressions.get(instruction.operands[2]);
                    expression = String.format("(%s %s %s)", operand1Expression, operation, operand2Expression);
                }

            //endregion


            // aktualisiert Registerausdruck
            registerExpressions.put(targetRegister, expression);
        }

        // Das letzte Zielregister enthält das Endergebnis
        String finalExpression = registerExpressions.get(lastWrittenRegister);
        function.append(finalExpression);

        return function.toString();
    }

    
    /***
     * For printing the fitness cases.
     * @return A string describing the fitness function including the fitness cases.
     */
    @Override
    public String toString() {
        String result = "# FitnessFunction: FitnessRegression \n"
                + "#  numberOfFitnessCases: \t" + numberOfFitnessCases + "\n"
                + "#  targetFunction:     \t" + "f(x) = " + targetFunction + "\n";
        for (int i = 0; i < numberOfFitnessCases; i++) {
            for (double x : fitnessCasesInput.get(i)) {
                result += " " + x;
            }
            result += " --> " + fitnessCasesOutput.get(i) + "\n";
        }
        return result;
    }

}
