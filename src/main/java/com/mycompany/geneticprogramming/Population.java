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
    HashMap<Individual, FitnessCacheEntry> diverseIndividuals;

    /**
     * computes the HashMap of every different Individual, their amount and fitness
     * equality is checked with toArithmetic() (--> Program)
     *
     * @return
     */
    public void computeFitnessAndDiversity(FitnessFunction fitnessFunction) {
        // Verwende diverseIndividuals, um Fitness und Vorkommen zu speichern
        this.diverseIndividuals = new HashMap<>();

        for (Individual individual : this) {
            // Überprüfe, ob das Programm bereits berechnet wurde
            if (diverseIndividuals.containsKey(individual)) {
                FitnessCacheEntry entry = diverseIndividuals.get(individual);
                individual.setFitnessMSE(entry.getFitness());
                entry.incrementCount();
            } else {
                // Berechne die Fitness und speichere sie im Cache
                double fitness = fitnessFunction.evalMSE(individual.getProgram());
                individual.setFitnessMSE(fitness);
                diverseIndividuals.put(individual, new FitnessCacheEntry(fitness));
            }
        }

        // Berechne die Diversity der Population
        this.computeDiversity();
    }



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
     * sets the Diversity of the Population
     *
     * @return
     */
    public void computeDiversity() {
        diversity = (double) diverseIndividuals.size() / this.size();
    }

    /*public void applyFitnessSharing() {
        for (Individual individual : this) {
            int nicheCount = diverseIndividuals.get(individual).getCount(); // Get how many times this individual appears
            double originalFitness = individual.getFitnessMSE(); // Assume getFitnessMSE() returns the fitness
            double sharedFitness = originalFitness * (double) nicheCount; // Apply fitness sharing
            individual.setFitnessShared(sharedFitness); // Store the shared fitness in the individual
        }
    }*/
}
