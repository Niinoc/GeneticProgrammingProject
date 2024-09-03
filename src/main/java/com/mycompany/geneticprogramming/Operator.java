/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Enum.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.function.Function;

/**
 * Operators used by the GP system to make a Program.
 * You can add new operators here, but note that in the current version three operands are expected.
 * One for target register and two for computing the new value.
 * An operator might only use a single input.
 * But, if you need one or three inputs also the interpreter must be changed.
 * @author Peter & Nicholas
 */
public enum Operator {

    ADD("+", 3),
    SUB("-", 3),
    MUL("*", 3),
    DIV("/", 3),
    NEG("-", 2),
    INV("1/", 2),
    SQRT("sqrt", 2),
    EXP("**", 3),
    LN("ln", 2),
    SIN("sin", 2),
    ARCSIN("asin", 2),
    COS("cos", 2),
    TAN("tan", 2),
    TANH("tanh", 2);

    final String name;
    final int numberOfOperands;

    Operator(String name, int numberOfOperands) {
        this.name = name;
        this.numberOfOperands = numberOfOperands;
    }

    /***
     * Returns a randomly selected operator.
     * @return A random operator.
     */
    public static Operator random() {
        return Operator.values()[MyRandom.nextInt(Operator.values().length)];
    }

    @Override
    public String toString() {
        return name;
    }
}

/*PI("3.141592*", input -> Math.PI * input[0], 2),
    EUL("e*", input -> Math.E * input[0], 2),
    HALF("0.5*", input -> 0.5 * input[0], 2),
    negHALF("-0.5*", input -> 0.5 * input[0], 2),
    ONE("1*", input -> 1.0 * input[0], 2),
    negONE("-1*", input -> 1.0 * input[0], 2),
    TWO("2*", input -> 2.0 * input[0], 2),
    negTWO("-2*", input -> 2.0 * input[0], 2),
    THREE("3*", input -> 3.0 * input[0], 2),
    negTHREE("-3*", input -> 3.0 * input[0], 2),*/

//mehr mit konstanten