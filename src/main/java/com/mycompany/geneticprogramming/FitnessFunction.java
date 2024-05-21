/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

/**
 * The fitness function takes a program and returns a fitness
 * @author Peter
 */
abstract public class FitnessFunction extends Global{
    abstract public Double eval(Program program);
    abstract public int getNumberOfInputs();   // the number of inputs of the program
    abstract public String evalInputOutputBehavior(Program program);
    abstract public String toArithmetic(Program program);

}
