package com.mycompany.geneticprogramming;

public class FitnessCacheEntry {
    private int count;
    private Double fitness;

    public FitnessCacheEntry(Double fitness) {
        this.count = 1;
        this.fitness = fitness;
    }

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public void incrementCount() {
        this.count += 1;
    }

    public Double getFitness() {
        return fitness;
    }

    public void setFitness(Double fitness) {
        this.fitness = fitness;
    }
}

