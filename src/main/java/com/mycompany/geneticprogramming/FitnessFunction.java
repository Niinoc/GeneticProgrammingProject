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
    abstract public Double evalMSE(Program program);

    public abstract Double evalMAPE(Program program);

    abstract public Double evalR2(Program program);
    public abstract Double evalEVS(Program program);
    abstract public String evalInputOutputBehavior(Program program);

}
