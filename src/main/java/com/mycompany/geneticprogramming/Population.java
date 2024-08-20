/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.ArrayList;
import java.util.HashMap;

/**
 * A population of programs.
 * It is simply an ArryList of Individuals.
 *
 * @author Peter & Nicholas
 */
public class Population extends ArrayList<Individual> {
    double diversity;
    HashMap<Individual, Integer> diverseIndividuals;

    @Override
    public String toString() {
        String result = "----- Population ------ \n";
        for (Individual individual : this)
            result += individual + " - - - - - - - - - \n";
        result += "----------------------\n";
        return result;
    }

    /**
     * @return the best individual from the population. That is, the individual with the lowest fitness.
     */
    public Individual best() {
        Individual bestIndividual = this.get(0);
        for (Individual individual : this) {
            if (individual.getFitnessMSE() < bestIndividual.getFitnessMSE())
                bestIndividual = individual;
        }
        return bestIndividual;
    }


    /**
     * sets the HashMap of every different Individual and their amount
     * equality is checked with toArithmetic() (--> Program)
     *
     * @return
     */
    public void computeDiversityMap() {
        HashMap<Individual, Integer> diversPrograms = new HashMap<>();
        for (Individual individual : this) {
            if (diversPrograms.containsKey(individual)) {
                diversPrograms.put(individual, diversPrograms.get(individual) + 1);
            } else {
                diversPrograms.put(individual, 1);
            }
        }
        diverseIndividuals = diversPrograms;
    }

    /**
     * sets the Diversity of the Population
     *
     * @return
     */
    public void computeDiversity() {
        diversity = (double) diverseIndividuals.size() / this.size();
    }

    public void applyFitnessSharing() {
        for (Individual individual : this) {
            int nicheCount = diverseIndividuals.get(individual); // Get how many times this individual appears
            double originalFitness = individual.getFitnessMSE(); // Assume getFitnessMSE() returns the fitness
            double sharedFitness = originalFitness * (double) nicheCount; // Apply fitness sharing
            individual.setFitnessShared(sharedFitness); // Store the shared fitness in the individual
        }
    }
}
