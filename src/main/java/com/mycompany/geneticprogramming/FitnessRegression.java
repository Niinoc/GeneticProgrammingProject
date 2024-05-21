/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.HashMap;
import java.util.Map;




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
    double[][] fitnessCasesInput = new double[numberOfFitnessCases][numberOfInputs];
    double[] fitnessCasesOutput = new double[numberOfFitnessCases];

    /**
     * *
     * The target function of the one-dimensional regression problem.
     * This is what we try to find. 
     * @param x Input value
     * @return Output value
     */
    double targetFunction(String function, double x) {      //TODO schafft einfach keine konstanten ordentlich, bzw sind überraschend schwer
        return x*x*x + 0.5*x*x + 1;                         // 1 / (x*x*x) erreicht fitness = infinity
    }

    /***
     * Instantiate a fitness function by generating a number of fitness cases.
     * A fitness case is one desired input-output pair.
     */
    public FitnessRegression() {        //TODO: wurzel, log, 1/x haben NAN ergebnisse -> kann nicht damit umgehen
        // create fitness cases
        for (int i = 0; i < numberOfFitnessCases; i++) {
            double input = (double) (i - numberOfFitnessCases / 2) * 0.1;   //anpassung von mir -> variabel
            double output = targetFunction(targetFunction, input);
            fitnessCasesInput[i][0] = input;
            fitnessCasesOutput[i] = output;
        }
    }

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
    public Double eval(Program program) {
        interpreter = new Interpreter(program); // instantiate an interpreter that runs the program

        double errorSum = 0;  // here we collect the error the program makes on the fitness cases
        for (int i = 0; i < numberOfFitnessCases; i++) { // For each fitness case
            double error = interpreter.run(fitnessCasesInput[i]) - fitnessCasesOutput[i];  // Run the program
            errorSum += error * error;    // And compare the output of the program with the desired output.                
        }
        return errorSum / numberOfFitnessCases;  //return the average error as the fitness
    }

    
    /*** 
     * Computes the input output behavior of the program in the same way as the fitness is evaluated.
     * Can be used to make a plot what we have learned.
     * @param program
     * @return All input output pairs used for fitness calculation. The last column is the target value.
     */
 
    @Override
    public String evalInputOutputBehavior(Program program) {
        String result = "";
        interpreter = new Interpreter(program); // instantiate an interpreter that runs the program

        double[] inputs = new double[numberOfFitnessCases];                 //für plotter
        double[] outputs = new double[numberOfFitnessCases];                //für plotter

        for (int i = 0; i < numberOfFitnessCases; i++) { // For each fitness case
            for (double input : fitnessCasesInput[i]) {
                result += input + "\t";
                inputs[i] = input;                                          //für plotter
            }
            result += interpreter.run(fitnessCasesInput[i]) + "\t";
            result += fitnessCasesOutput[i] + "\n";

            outputs[i] = interpreter.run(fitnessCasesInput[i]);             //für plotter

        }

//        new GraphPlotter(inputs, outputs, fitnessCasesOutput);  //TODO für java plot entkommentieren

        return result;  //return the average error as the fitness
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

        // Auswertung der Anweisungen
        for (Instruction instruction : program.instructions) {

            int targetRegister = instruction.operands[0];

            //region baut Ausdruck
                Operator operator = instruction.operator;
                String operation = operator.toString();
                // Ausdrücke für Operanden
                String operand1Expression = registerExpressions.get(instruction.operands[1]);
                String operand2Expression = registerExpressions.get(instruction.operands[2]);
            //endregion


            // aktualisiert Registerausdruck
            String expression = String.format("(%s %s %s)", operand1Expression, operation, operand2Expression);
            registerExpressions.put(targetRegister, expression);
        }

        // Der letzte Zielregister enthält das Endergebnis
        String finalExpression = registerExpressions.get(program.getNumberOfRegisters() - 1);
        function.append(finalExpression);

        return function.toString();
    }

    
    /***
     * For printing the fitness cases.
     * @return A string describing the fitness function including the fitness cases.
     */
    @Override
    public String toString() {
        String result = "FitnessFunction: FitnessRegression \n"
                + "#  numberOfFitnessCases: \t" + numberOfFitnessCases + "\n"
                + "#  targetFunction:     \t" + "f(x) = " + targetFunction + "\n";
        for (int i = 0; i < numberOfFitnessCases; i++) {
            for (double x : fitnessCasesInput[i]) {
                result += " " + x;
            }
            result += " --> " + fitnessCasesOutput[i] + "\n";
        }
        return result;
    }

}
