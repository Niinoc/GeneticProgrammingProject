/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.ArrayList;

/**
 * An Interpreter can run a Program for a given input.
 * The Interpreter is somehow equivalent to a CPU.
 * The input is written to the first registers.
 * The output is the last written register.
 * @author Peter
 */
public class Interpreter {

    Program program;
    double[] registers;

    /***
     * Instantiate an interpreter (CPU) for a given program.
     * This includes the generation of the required registers.
     * @param program 
     */
    public Interpreter(Program program) {
        this.program = program;
        this.registers = new double[program.getNumberOfRegisters()];
    }

    /***
     * Runs the program for a given input (vector).
     * 
     * @param input
     * @return 
     */
    double run(ArrayList<Double> input) {
        // Initialize registers according to the program.
        for (int i = 0; i < program.getNumberOfRegisters(); i++) {
            registers[i] = program.initialRegisterStates[i];
        }
        // Write input into registers (hoping that there are enough registers :-)
        for (int i = 0; i < input.size(); i++) {
            registers[i] = input.get(i);
        }
        // Run instructions
        int targetRegister = 0;  // just some initialization so that empty programs can be exectuted.
        for (Instruction instruction : program.instructions) {
            Operator operator = instruction.operator;
            targetRegister = instruction.operands[0];
            Double[] operandValues;
            if (operator.numberOfOperands == 2) {
                operandValues = new Double[]{
                        registers[instruction.operands[1]]
                };
            } else {
                operandValues = new Double[]{
                        registers[instruction.operands[1]],
                        registers[instruction.operands[2]]
                };
            }
            registers[targetRegister] = instruction.operator.function.apply(operandValues);

        }
        return registers[targetRegister]; // Return the value from the last target register written to.
    }


}
