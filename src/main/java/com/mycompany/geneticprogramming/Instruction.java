/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;
import java.util.Arrays;
import java.util.Objects;
import java.util.Random;

/**
 * An Instruction is one row of our program, e.g.  R3 := R0 + R5
 * @author Peter
 * 
 * To simplyfy things:
 * - there are only arithmetic instructions, for example:   R3 := R0 + R5
 * - There are always (at least) three operands, for example register 3, 0, 5
 * - The first operand (here, 3) is the target register, where the result is written to.
 * - The only addressing mode is by registers, so constant values have to be stored in a register first.
 *    (Sorry, this might not be a good design decission,because we need two 
 *     types of mutations: mutation of instructions and mutation of initial register values)
 */
public class Instruction extends Global{

    Operator operator;
    int[] operands; // Register ids of the operands. 
                    // Here, exactly three registers are used.
                    // Example: For  R2 = R1 + R3   operands = {2,1,3}

    
    /***
     * Constructor for a new instruction (one row of our program).
     * For example  R2 = R1 + R3
     *   new Instruction(Operator.ADD, 2, 1, 3);
     * @param operator
     * @param operands 
     */
    
    Instruction(Operator operator, int... operands) {  // nice syntatic sugar to pass a variable number of arguments
        this.operator = operator;
        this.operands = operands;
    }
    
    /***
     * Returns a new randomly generated instruction.
     * Uses the global variable numberOfRegisters and fitnessFunction.
     * The generated instruction does not overwrite input registers.
     * Note that the first numberOfInputs registers are taken as input registers.
     * @return The new instruction generated.
     */
    public static Instruction random() {
        Operator op = Operator.random();
        if (op.numberOfOperands >= 2) {
            return new Instruction(Operator.random(),
                    MyRandom.nextInt(numberOfRegisters - numberOfInputs) + numberOfInputs, // do not allow the input to be overwritten
                    MyRandom.nextInt(numberOfRegisters),
                    (MyRandom.nextInt(numberOfRegisters))
            );
        }
        else {
            return new Instruction(Operator.random(),
                    MyRandom.nextInt(numberOfRegisters - numberOfInputs) + numberOfInputs, // do not allow the input to be overwritten
                    MyRandom.nextInt(numberOfRegisters)
            );
        }
    }

    /**
     * provides important functionality for HashMap
     * @return
     */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Instruction that = (Instruction) obj;
        return operator == that.operator && Arrays.equals(operands, that.operands);
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(operator);
        result = 31 * result + Arrays.hashCode(operands);
        return result;
    }

    @Override
    public String toString(){
        if (operator.numberOfOperands == 3)
            return "R[" + operands[0] + "] = " + "R[" + operands[1] 
                    + "] " + operator + " " 
                    + "R[" + operands[2] + "];";
        if (operator.numberOfOperands == 2)
            return "R[" + operands[0] + "] = " + operator + " "
                    + "R[" + operands[1] + "];";
        return "UNKOWN_NUMBER_OF_OPERANDS: " + operands.length;
    }
    
    public static void test(){
        System.out.println(random());  // prints a random instructions
    }
}
