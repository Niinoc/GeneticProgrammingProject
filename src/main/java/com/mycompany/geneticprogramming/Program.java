/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.*;
import java.util.function.Function;

/**
 * A Program consists of initial values for each register and a list of instructions.
 *   
 *
 * @author Peter
 */
public class Program extends Global {

    double[] initialRegisterStates;

    List<Instruction> instructions = new ArrayList<>();

    /**
     * *
     * Instantiate a program with no instructions.
     * Registers are created and initialize with 0.0.
     *
     * @param numberOfRegisters
     */
    public Program() {
        initialRegisterStates = new double[numberOfRegisters];
    }

    /**
     * Instantitate a copy (clone) of the program.
     * Copyconstructor, sollte man vermutlich anders machen ....
     *
     * @param program
     */
    public Program(Program program) {
        initialRegisterStates = new double[program.getNumberOfRegisters()];
        for (int i = 0; i < initialRegisterStates.length; i++) {
            initialRegisterStates[i] = program.initialRegisterStates[i];
        }
        instructions = new ArrayList<>(program.instructions); // clone the instructions
    }

    /**
     * *
     * The number of registers used by the program. Note that this value should
     * be the same as the global parameter numberOfRegisters. [Das sollte man
     * noch vereinfachen ....]
     *
     * @return The number of registers used by the program.
     */
    public int getNumberOfRegisters() {
        return initialRegisterStates.length;
    }

    /**
     * *
     * Returns a random program of a given length.
     *
     * @param size of the program generated.
     * @param numberOfRegisters the number of registeres that can be used
     * @return The randomly generated program.
     *
     */
    public static Program random(int size) {
        Program program = new Program(); // Instantiate an empty program
        // Generate random initial states for the registers of the program
        for (int i = 0; i < numberOfRegisters; i++) {
            program.initialRegisterStates[i] = randomRegisterValue(-1.0, 1.0);
        }
        // Generate random instructions
        for (int i = 0; i < size; i++) {
            program.instructions.add(Instruction.random());
        }
        return program;
    }

    /**
     * *
     * Computes a random initial state for a register.
     *
     * @return Random value to be used to initialize a register.
     */
    public static Double randomRegisterValue() {
        return MyRandom.nextDouble() * 2.0 - 1.0;  // TODO: SHOULD BE A PARAMETER
    }
    public static Double randomRegisterValue(double minValue, double maxValue) {
        return minValue + (MyRandom.nextDouble() * (maxValue - minValue));
    }

    /**
     * provides important functionality for HashMap
     * @return
     */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Program that = (Program) obj;
        return Objects.equals(this.toArithmetic(), that.toArithmetic());    //just evaluates the symbolic form -> no introns
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(this.toArithmetic());
        return result;
    }


    @Override
    public String toString() {
        String result = "initialRegisterState: ";
        for (int i = 0; i < initialRegisterStates.length; i++) {
            result += "\nR[" + i + "] = " + initialRegisterStates[i] + ";  ";
        }
        for (Instruction instruction : instructions) {  // das geht sicher eleganter in einer zeile :-)
            result += "\n" + instruction;
        }
        return result;
    }

    public String toArithmetic() {
        StringBuilder function = new StringBuilder();

        // Mapping für die Registerausdrücke
        Map<Integer, String> registerExpressions = new HashMap<>();

        // Initialisierung der Ausdrücke für die Eingaberegister
        for (int i = 0; i < numberOfInputs; i++) {
            registerExpressions.put(i, "x_" + i);
        }
        for (int i = numberOfInputs; i < this.getNumberOfRegisters(); i++) {
            registerExpressions.put(i, String.valueOf((this.initialRegisterStates[i])));
        }

        int lastWrittenRegister = 0;

        // Auswertung der Anweisungen
        for (Instruction instruction : this.instructions) {

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

}
