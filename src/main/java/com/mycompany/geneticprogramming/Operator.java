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
        ADD("+", input -> input[0] + input[1]),
        SUB("-", input -> input[0] - input[1]),
        MUL("*", input -> input[0] * input[1]),
        DIV("/", input -> input[1] != 0 ? input[0] / input[1] : 0), // protected division
//        NEG("-x", input -> -(input[0])),
//        INV("1/x", input -> 1/(input[0])),
//        SQRT("sqrt", input -> Math.sqrt(input[0])),
//        EXP("^", input -> Math.pow(input[0], input[1]),
//        LOG("log", input -> Math.log(input[0]), //unterschiedliche log?
//        SIN("sin", input -> Math.sin(input[0]),
//        COS("cos", input -> Math.cos(input[0]),
//        TAN("tan", input -> Math.tan(input[0]),
    //iwas mit e
    //iwas mit konstanten
        ;

        final String name;
        final Function<Double [],Double> function; 
        Operator (String name, Function<Double [], Double> function) {
            this.name = name;
            this.function = function;
        };
        
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
