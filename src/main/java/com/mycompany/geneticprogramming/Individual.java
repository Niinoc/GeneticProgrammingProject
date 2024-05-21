/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

/**
 * An individual consists of a program and a fitness.
 * @author Peter
 * Later we can add further parameters to an invidual, like a mutation strength.
 */
public class Individual {
    public Program program;
    public Double fitness;

    public Individual(Program program, Double fitness) {
        this.program = program;
        this.fitness = fitness;
    }

    public Program getProgram() {
        return program;
    }

    public Double getFitness() {
        return fitness;
    }
    
    @Override
    public String toString(){
        return "Individual with fitness " + getFitness() + "\n"+ program + "\n";        
    }
    
}
