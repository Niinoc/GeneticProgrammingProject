/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.util.Random;

/**
 *
 * @author Peter
 */
/**
 * *
 * This class provides random numbers. The class encapsulates the JAVA random
 * number generator class Random. So, we can easily change the RNG later and
 * also have control over the random number generator. Note that the quality
 * (and efficiency) of random numbers is critical in heuristic algorithms like
 * genetic programing, in particular in parallel environments.
 *
 * @author Peter
 */
public class MyRandom extends Global{

    static Random random = new Random(seed); // Set the seed

    /***
     * Returns a random value from [0, 1]
     * @return Random double from [0,1]
     */
    public static double nextDouble() {
        return random.nextDouble();
    }

    
    /***
     * Returns random integers from {origin, origin +1 , ..., bound -1}
     * @param origin
     * @param bound
     * @return 
     */
    public static int nextInt(int origin, int bound) {
        return origin + random.nextInt(bound - origin);
    }
    
    /***
     * A random integer from {0, 1, ..., bound-1}
     * @param bound 
     * @return 
     */
    public static int nextInt(int bound) {
        return random.nextInt(bound);
    }
    
    public static void test(){ 
        for (int i=0;i<20;i++){
            System.out.println(nextInt(5, 7));
        }
    }

}
