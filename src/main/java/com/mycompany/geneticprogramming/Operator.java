/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Enum.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.function.Function;

/**
 * Operators used by the GP system to make a Program.
 * You can add new operators here, but note that in the current version three operands are expected.
 * One for target register and two the computing the new value.
 * An operator might only use a single input.
 * But, if you need three inputs also the interpreter must be changed.
 * @author Peter
 */
public enum Operator {
    ADD("+", input -> input[0] + input[1], 3),
    SUB("-", input -> input[0] - input[1], 3),
    MUL("*", input -> input[0] * input[1], 3),
    DIV("/", input -> input[1] != 0 ? input[0] / input[1] : 0, 3), // Geschützte Division
    NEG("-", input -> -(input[0]), 2),
    INV("1/", input -> input[0] != 0 ? 1 / input[0] : 0, 2), // Geschützte Inversion
    SQRT("sqrt", input -> input[0] >= 0 ? Math.sqrt(input[0]) : 0, 2), // Geschützte Quadratwurzel
    EXP("**", input -> Math.pow(input[0], input[1]), 3),
    LOG("log", input -> input[0] > 0 ? Math.log(input[0]) : 0, 2), // Geschützter Logarithmus (nur für positive Werte)
    SIN("sin", input -> Math.sin(input[0]), 2),
    COS("cos", input -> Math.cos(input[0]), 2),
    TAN("tan", input -> Math.tan(input[0]), 2);
    //iwas mit e
    //iwas mit konstanten
        ;

    final String name;
    final Function<Double [],Double> function;
    final int numberOfOperands;

    Operator (String name, Function<Double [], Double> function, int numberOfOperands) {
        this.name = name;
        this.function = function;
        this.numberOfOperands = numberOfOperands;
    }

    /***
     * Returns a randomly selected operator.
     * @return A random operator.
     */
    public static Operator random(){
        return Operator.values()[MyRandom.nextInt(Operator.values().length)];
    }

    @Override
        public String toString(){
            return name;
        }

}
