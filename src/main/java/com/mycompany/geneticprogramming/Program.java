/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.*;

/**
 * A Program consists of initial values for each register and a list of instructions.
 *   
 *
 * @author Peter & Nicholas
 */
public class Program extends Global {

    double[] initialRegisterStates;

    static double[] constants = {
            -5.0, -4.0, -3.0, -2.0, -1.0, -0.5, 0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0,
            Math.PI, Math.E, Math.sqrt(2), Math.sqrt(3), Math.log(2), Math.log(10),
            Math.log10(Math.E), (1 + Math.sqrt(5)) / 2, // phi
            0.25, 0.75, 1.5, -1.5, 1/Math.sqrt(2),
            0.5772,         // Euler's constant
            Math.PI * Math.PI / 6, // zeta(2)
            1.20206,        // zeta(3)
            3e8,            // c - Lichtgeschwindigkeit
            6.674e-11,      // G - Gravitationskonstante
            6.626e-34,      // h - Plancksches Wirkungsquantum
            1.381e-23,      // k_B - Boltzmann-Konstante
            8.854e-12       // epsilon_0 - Elektrische Feldkonstante
    };

    List<Instruction> instructions = new ArrayList<>();

    /**
     * *
     * Instantiate a program with no instructions.
     * Registers are created and initialize with 0.0.
     *
     * @param numberOfRegisters
     */
    public Program() {
        initialRegisterStates = new double[numberOfFreeRegisters];
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
        for (int i = 0; i < numberOfFreeRegisters; i++) {
            program.initialRegisterStates[i] = randomRegisterValue();
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
    public static double randomRegisterValue() {
        return constants[(MyRandom.nextInt(constants.length))];
    }

    /**
     * provides important functionality for HashMap
     * @return
     */

    private String cachedArithmeticForm;
    private Integer cachedHashCode;

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Program that = (Program) obj;
        return Objects.equals(this.getArithmeticForm(), that.getArithmeticForm());
    }

    @Override
    public int hashCode() {
        if (cachedHashCode == null) {
            cachedHashCode = Objects.hash(this.getArithmeticForm());
        }
        return cachedHashCode;
    }

    public String getArithmeticForm() {
        if (cachedArithmeticForm == null) {
            cachedArithmeticForm = this.toArithmetic();
        }
        return cachedArithmeticForm;
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

    /**
     *
     * @return the arithmetic form of the Program aka it's Instructions
     * @author Nicholas
     */
    public String toArithmetic() {
        // Mapping für die Registerausdrücke
        Map<Integer, String> registerExpressions = new HashMap<>(this.getNumberOfRegisters());

        // Initialisierung der Ausdrücke für die Eingaberegister
        for (int i = 0; i < numberOfInputs; i++) {
            registerExpressions.put(i, "x_" + i);
        }
        for (int i = numberOfInputs; i < this.getNumberOfRegisters(); i++) {
            registerExpressions.put(i, Double.toString(this.initialRegisterStates[i]));
        }

        int lastWrittenRegister = 0;

        // Auswertung der Anweisungen
        for (Instruction instruction : this.instructions) {
            int targetRegister = instruction.operands[0];
            lastWrittenRegister = targetRegister;

            // Operator-String erstellen
            String operation = instruction.operator.toString();

            // Ausdrücke für Operanden
            String operand1Expression = registerExpressions.get(instruction.operands[1]);
            String operand2Expression = null; // Nur initialisieren, wenn notwendig
            StringBuilder expressionBuilder = new StringBuilder();

            if (instruction.operator.numberOfOperands == 2) {
                expressionBuilder.append(operation).append("(").append(operand1Expression).append(")");
            } else {
                operand2Expression = registerExpressions.get(instruction.operands[2]);
                expressionBuilder.append("(")
                        .append(operand1Expression)
                        .append(" ")
                        .append(operation)
                        .append(" ")
                        .append(operand2Expression)
                        .append(")");
            }

            // Speichern des erstellten Ausdrucks in der Register-Map
            registerExpressions.put(targetRegister, expressionBuilder.toString());
        }

        return registerExpressions.get(lastWrittenRegister);
    }


}
