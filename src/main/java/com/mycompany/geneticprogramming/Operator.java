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
 * @author Peter & Nicholas
 */
public enum Operator {
    ADD("+", input -> input[0] + input[1], 3),
    SUB("-", input -> input[0] - input[1], 3),
    MUL("*", input -> input[0] * input[1], 3),
    DIV("/", input -> input[1] != 0 ? input[0] / input[1] : 0, 3), // Geschützte Division

    NEG("-", input -> -(input[0]), 2),
    INV("1/", input -> input[0] != 0 ? 1 / input[0] : 0, 2), // Geschützte Inversion

    SQRT("sqrt", input -> input[0] >= 0 ? Math.sqrt(input[0]) : 0, 2), // Geschützte Quadratwurzel
    EXP("**", input -> {
        if (input[0] == 0) return (input[1] > 0) ? 0 : Math.pow(10.0, 8.0);  // 0^positive = 0, 0^negative = "Infinity"

        else if (input[0] < 0 && input[1] % 1 != 0) return 0.0;  // negative base and non-integer exponent result in NaN, handle as 0

        else return Math.pow(input[0], input[1]);
    }, 3),
    LN("ln", input -> input[0] > 0 ? Math.log(input[0]) : 0, 2), // Geschützter Logarithmus (nur für positive Werte)

    SIN("sin", input -> Math.sin(input[0]), 2),
//    ARCSIN("arcsin", input -> Math.asin(input[0]), 2),
    COS("cos", input -> Math.cos(input[0]), 2),
//    ARCCOS("arccos", input -> Math.acos(input[0]), 2),
    TAN("tan", input -> Math.tan(input[0]), 2),
//    ARCTAN("arctan", input -> Math.atan(input[0]), 2),

    PI("3.141592*", input -> Math.PI*(input[0]), 2),
    EUL("e^", input -> Math.exp(input[0]), 2),

    //mehr mit konstanten
    ;

    /*ADD("+", input -> input[0] + input[1], 3),
    SUB("-", input -> input[0] - input[1], 3),
    MUL("*", input -> input[0] * input[1], 3),
    DIV("/", input -> input[0] / input[1], 3),

    NEG("-", input -> -(input[0]), 2),
    INV("1/", input -> 1 / input[0], 2),

    SQRT("sqrt", input -> Math.sqrt(input[0]), 2),
    EXP("**", input -> Math.pow(input[0], input[1]), 3),
    LN("ln", input ->  Math.log(input[0]), 2),

    SIN("sin", input -> Math.sin(input[0]), 2),
    //    ARCSIN("arcsin", input -> Math.asin(input[0]), 2),
    COS("cos", input -> Math.cos(input[0]), 2),
    //    ARCCOS("arccos", input -> Math.acos(input[0]), 2),
    TAN("tan", input -> Math.tan(input[0]), 2),
//    ARCTAN("arctan", input -> Math.atan(input[0]), 2),

    PI("3.141592*", input -> Math.PI*(input[0]), 2),
    EUL("e^", input -> Math.exp(input[0]), 2),

    //mehr mit konstanten
    ;*/

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
