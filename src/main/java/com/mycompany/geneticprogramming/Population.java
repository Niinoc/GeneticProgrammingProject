/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.ArrayList;

/**
 * A population of programs.
 * It is simply an ArryList of Individuals.
 * @author Peter
 * 
 * 
 * 
 */
public class Population extends ArrayList<Individual> {
    @Override
    public String toString(){
        String result = "----- Population ------ \n";
        for (Individual individual : this)
            result += individual + " - - - - - - - - - \n";
        result += "----------------------\n";
        return result;
    }
    
    /***
     * Returns the best individual from the population. That is, the individual with the lowest fitness.
     * @return 
     */
    public Individual best(){
        Individual bestIndividual = this.get(0);
        for (Individual individual : this){
            if (individual.getFitness() < bestIndividual.getFitness())
                bestIndividual = individual;
        }
        return bestIndividual;
    }
}
