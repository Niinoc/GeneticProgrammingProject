/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.Objects;

/**
 * An individual consists of a program and a fitness.
 * @author Peter
 * Later we can add further parameters to an invidual, like a mutation strength.
 */
public class Individual {
    public Program program;
    public Double fitnessMSE;
    public Double fitnessR2;
    public Double fitnessEVS;
    public Double fitnessMAPE;

public Individual(Program program, Double fitnessMSE, Double fitnessR2, Double fitnessEVS, Double fitnessMAPE) {
        this.program = program;
        this.fitnessMSE = fitnessMSE;
        this.fitnessR2 = fitnessR2;
        this.fitnessEVS = fitnessEVS;
        this.fitnessMAPE = fitnessMAPE;
    }

    public Individual(Program program, Double fitnessMSE) {
        this.program = program;
        this.fitnessMSE = fitnessMSE;
    }

    public Program getProgram() {
        return program;
    }

    public Double getFitnessMSE() {
        return fitnessMSE;
    }

    public Double getFitnessR2() {
        return fitnessR2;
    }

    public Double getFitnessEVS() {
        return fitnessEVS;
    }

    public Double getFitnessMAPE() {
        return fitnessMAPE;
    }

    /**
     * provides important functionality for HashMap
     * @return
     */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Individual that = (Individual) obj;
        return Objects.equals(program, that.program);
    }

    @Override
    public int hashCode() {
        return Objects.hash(program);
    }

    @Override
    public String toString(){
        return "MSE fitness " + getFitnessMSE() + "\n"
//                + "R2 Score " + getFitnessR2() + "\n"
//                + "Explained Varianz Score " + getFitnessEVS() + "\n"
//                + "MAPE Score " +getFitnessMAPE() + "\n"      //TODO entkommentieren für weitere Maße
                + program + "\n";
    }

}
