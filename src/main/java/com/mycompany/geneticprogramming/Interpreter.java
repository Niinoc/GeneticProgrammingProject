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

    public Program getProgram() {
        return program;
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
        // Write input into registers
        for (int i = 0; i < input.size(); i++) {
            registers[i] = input.get(i);
        }

        int targetRegister = 0;  // initialization
        for (Instruction instruction : program.instructions) {
            targetRegister = instruction.operands[0];
            Operator operator = instruction.operator;

            switch (operator) {
                case ADD ->
                        registers[targetRegister] = registers[instruction.operands[1]] + registers[instruction.operands[2]];
                case SUB ->
                        registers[targetRegister] = registers[instruction.operands[1]] - registers[instruction.operands[2]];
                case MUL ->
                        registers[targetRegister] = registers[instruction.operands[1]] * registers[instruction.operands[2]];
                case DIV ->
                        registers[targetRegister] = registers[instruction.operands[1]] / registers[instruction.operands[2]];
                case NEG -> registers[targetRegister] = -registers[instruction.operands[1]];
                case INV -> registers[targetRegister] = 1.0 / registers[instruction.operands[1]];
                case SQRT -> registers[targetRegister] = Math.sqrt(registers[instruction.operands[1]]);
                case EXP ->
                        registers[targetRegister] = Math.pow(registers[instruction.operands[1]], registers[instruction.operands[2]]);
                case LN -> registers[targetRegister] = Math.log(registers[instruction.operands[1]]);
                case SIN -> registers[targetRegister] = Math.sin(registers[instruction.operands[1]]);
                case COS -> registers[targetRegister] = Math.cos(registers[instruction.operands[1]]);
                case TAN -> registers[targetRegister] = Math.tan(registers[instruction.operands[1]]);

                // Füge weitere Operatoren hier hinzu
                default -> throw new UnsupportedOperationException("Unknown operator: " + operator);
            }
        }
        return registers[targetRegister];
    }


}
